<script lang="ts">
  import Tooltip, { Wrapper } from "@smui/tooltip";
  import {
    calculateElapsed,
    calculateAge,
    mapImage,
    handleError,
    repoToString,
    readableDateTime,
    parseDateTime,
    isJobComplete,
    getVersionLink,
  } from "../ts/utils";
  import NewJobForm from "./NewJobForm.svelte";
  import { submitNewJob } from "../ts/jobs";
  import type { ArtifactUrl, Book, Repository, Status } from "../ts/types";
  import { onMount } from "svelte";
  import DataTable, {
    Head,
    Body,
    Row,
    Cell,
    SortValue,
    Pagination,
  } from "@smui/data-table";
  import Select, { Option } from "@smui/select";
  import IconButton from "@smui/icon-button";
  import { Label } from "@smui/common";
  import Button from "@smui/button";
  import { repoSummariesStore, jobsStore, ABLStore } from "../ts/stores";

  import type { Config, Job, JobType } from "../ts/types";
  import DetailsDialog from "./DetailsDialog.svelte";
  import { MINUTES, SECONDS } from "../ts/time";
  import { hasABLEntry } from "../ts/abl";
  import ApprovedBooksDialog from "./ApprovedBooksDialog.svelte";
  import VersionLink from "./VersionLink.svelte";
  import { ProcessConfig } from "../ts/config";

  const config: Config = ProcessConfig.fromEnv(process.env);

  let statusStyles = {
    queued: "filter-yellow",
    assigned: "filter-yellow pulse",
    processing: "filter-yellow rock",
    failed: "filter-red",
    completed: "filter-green",
    aborted: "filter-red",
  };

  let selectedJobTypes = [];

  let detailsOpen = false;
  let ablOpen = false;
  let selectedJob: Job;

  let selectedRepo: string;
  let selectedBook: string;

  // Initialization
  let jobs: Job[] = [];
  let slice: Job[] = [];
  let sort: keyof Job = "id";
  let sortDirection: Lowercase<keyof typeof SortValue> = "descending";

  const jobStartRateLimitDurationMillis = 1000;
  let lastJobStartTime = Date.now();

  enum JobTypeId {
    PDF = 3,
    Web = 4,
    Docx = 5,
    EPUB = 6,
  }

  // Job creation
  async function clickNewJob(
    selectedRepo,
    selectedBook,
    selectedVersion,
    selectedJobTypes,
  ) {
    if (lastJobStartTime + jobStartRateLimitDurationMillis > Date.now()) {
      return;
    }
    lastJobStartTime = Date.now();
    await Promise.all(
      selectedJobTypes.map((jobType) => {
        submitNewJob(
          JobTypeId[jobType as number],
          selectedRepo,
          selectedBook,
          selectedVersion,
        );
      }),
    );
    setTimeout(async () => {
      await Promise.all([
        jobsStore.updateImmediate(),
        repoSummariesStore.update(),
      ]);
    }, 1 * SECONDS);
  }

  function getStatusStyle(job: Job) {
    const statusName = job.status.name;
    let cssClasses = `job-status-icon ${statusStyles[statusName]}`;
    if (
      statusName === "completed" &&
      Date.now() - parseDateTime(job.updated_at) < 30 * SECONDS
    ) {
      cssClasses += " bounce";
    }
    return cssClasses;
  }

  function getVersionLinkFromJob(job: Job) {
    return getVersionLink(job.repository, job.version);
  }

  function handleHash() {
    const jobId = document.location.hash.slice(1);
    const job = jobs.find((j) => j.id === jobId);
    if (job) {
      const loc = document.location;
      selectedJob = job;
      detailsOpen = true;
      history.replaceState("", document.title, loc.pathname + loc.search);
      return true;
    } else if (jobs.length > 0) {
      handleError(new Error(`Could not find job "${jobId}"`));
      return true;
    }
    return false;
  }

  // Pagination
  let rowsPerPage = 10;
  let currentPage = 0;
  $: start = currentPage * rowsPerPage;
  $: end = Math.min(start + rowsPerPage, sortedRows.length);
  $: lastPage = Math.max(Math.ceil(sortedRows.length / rowsPerPage) - 1, 0);
  $: if (currentPage > lastPage) {
    currentPage = lastPage;
  }

  // Job filtering
  $: filteredRows = jobs.filter(
    (entry) =>
      (selectedJobTypes.length === 0 ||
        selectedJobTypes.some((id) =>
          entry.job_type.display_name.includes(id),
        )) &&
      (!selectedRepo ||
        repoToString(entry.repository).includes(selectedRepo)) &&
      (!selectedBook ||
        entry.books.find((item) => item.slug.includes(selectedBook)) != null),
  );

  // Job sorting
  $: sortedRows = filteredRows.sort((a: Job, b: Job) => {
    type ValueTypes =
      | number
      | string
      | Status
      | Repository
      | ArtifactUrl[]
      | Book[];
    let aVal: ValueTypes, bVal: ValueTypes;
    [aVal, bVal] = [a[sort], b[sort]][
      sortDirection === "ascending" ? "slice" : "reverse"
    ]();
    if (sort === "id") {
      aVal = parseInt(aVal as string);
      bVal = parseInt(bVal as string);
    } else if (sort === "repository") {
      aVal = repoToString(aVal as Repository);
      bVal = repoToString(bVal as Repository);
    } else if (sort === "job_type") {
      aVal = (aVal as JobType).display_name;
      bVal = (bVal as JobType).display_name;
    }
    if (typeof aVal === "string" && typeof bVal === "string") {
      return aVal.localeCompare(bVal);
    } else if (Array.isArray(aVal) && Array.isArray(bVal)) {
      // lexicographic string sort for books
      let a: string[];
      let b: string[];
      if (sort === "books") {
        a = aVal.map((b) => b.slug);
        b = bVal.map((b) => b.slug);
      } else {
        handleError(new Error(`Cannot handle list sort of ${sort}`));
        return 0;
      }
      if (a.length !== b.length) {
        return a.length - b.length;
      }
      for (let i = 0; i < a.length; i++) {
        const cmp = a[i].localeCompare(b[i]);
        if (cmp !== 0) {
          return cmp;
        }
      }
      return 0;
    }
    return Number(aVal) - Number(bVal);
  });

  $: slice = sortedRows.slice(start, end);

  onMount(async () => {
    const onJobsAvailable: Array<(jobs: Job[]) => boolean> = [];
    if (document.location.hash) {
      onJobsAvailable.push(handleHash);
    }
    jobsStore.subscribe((updatedJobs) => {
      jobs = updatedJobs;
      // Run each one until it returns true, then remove it
      onJobsAvailable
        .map((cb, idx): [boolean, number] => [cb(jobs), idx])
        .filter(([shouldRemove, _]) => shouldRemove)
        .forEach(([_, idx]) => onJobsAvailable.splice(idx, 1));
    });
    // Give job fetching priority over repoSummariesStore on page load
    jobsStore.update().then(() => {
      void repoSummariesStore.update();
      void ABLStore.startPolling(1 * MINUTES);
    });
    jobsStore.startPolling(10 * SECONDS);
    addEventListener("hashchange", handleHash);
    document.addEventListener("visibilitychange", (event) => {
      if (document.visibilityState === "visible") {
        jobsStore.startPolling(10 * SECONDS);
      } else if (document.visibilityState === "hidden") {
        jobsStore.stopPolling();
      }
    });
  });
</script>

<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px; padding-top: 8px;"
/>

<NewJobForm
  bind:selectedJobTypes
  bind:selectedRepo
  bind:selectedBook
  {clickNewJob}
/>

<div>
  <Button
    on:click={() => {
      ablOpen = true;
    }}
    data-control-type={"button-show-abl"}
  >
    Show ABL
  </Button>
</div>

<div>
  <DataTable
    responsive
    sortable
    stickyHeader
    bind:sort
    bind:sortDirection
    table$aria-label="Jobs list"
  >
    <Head>
      <Row>
        <Cell numeric columnId="id">
          <IconButton class="material-icons">arrow_upward</IconButton>
          <Label>Id</Label>
        </Cell>
        <Cell columnId="job_type">
          <Label>Type</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="repository" class="md">
          <Label>Repo</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="books">
          <Label>Book</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="version">
          <Label>Version</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="status" sortable={false}>
          <Label>Status</Label>
        </Cell>
        <Cell columnId="updated-at" class="md" sortable={false}>
          <Label>Elapsed/Created</Label>
        </Cell>
        <Cell columnId="worker-version" class="lg" sortable={false}>
          <Label>Worker Version</Label>
        </Cell>
        <Cell columnId="github-user" sortable={false}>
          <Label>User</Label>
        </Cell>
        <!-- <Cell columnId="approved" sortable={false}>
        <Label>Approved</Label>
      </Cell> -->
      </Row>
    </Head>
    <!-- <LinearProgress
    indeterminate
    bind:closed={open}
    aria-label="Data is being loaded..."
    slot="progress"
  /> -->
    <Body>
      {#each slice as item (item.id)}
        <!-- <DetailRow> -->
        {@const isApproved = hasABLEntry($ABLStore, item)}
        <Row slot="data" class={isApproved ? "abl" : ""}>
          <Cell>
            <Button
              data-control-type={"button-job-id"}
              on:click={() => {
                selectedJob = item;
                detailsOpen = true;
              }}
            >
              {item.id}
            </Button>
          </Cell>
          <Cell>
            <Wrapper>
              {#if isJobComplete(item)}
                <a
                  href={item.books.length === 1
                    ? item.artifact_urls[0].url
                    : `#${item.id}`}
                  target={item.books.length === 1 ? "_blank" : "_self"}
                  rel="noreferrer"
                >
                  <img
                    alt={item.job_type.display_name}
                    src={mapImage(
                      "job_type",
                      item.job_type.display_name,
                      "svg",
                    )}
                    class="job-type-icon"
                    data-is-complete="true"
                  />
                </a>
              {:else}
                <img
                  alt={item.job_type.display_name}
                  src={mapImage("job_type", item.job_type.display_name, "svg")}
                  class="job-type-icon"
                  data-is-complete="false"
                />
              {/if}
              <Tooltip>{item.job_type.display_name}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell class="md">
            <Wrapper>
              <span class="table-text repo"
                >{repoToString(item.repository)}</span
              >
              <Tooltip>{repoToString(item.repository)}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell>
            {#if item.books.length === 1}
              <Wrapper>
                <span class="table-text book">{item.books[0].slug}</span>
                <Tooltip>{item.books[0].slug}</Tooltip>
              </Wrapper>
            {:else}
              <Wrapper>
                <span class="table-text book">all</span>
                <Tooltip>
                  {#each item.books as book}
                    {book.slug}<br />
                  {/each}
                </Tooltip>
              </Wrapper>
            {/if}
          </Cell>
          <Cell>
            <VersionLink
              href={getVersionLinkFromJob(item)}
              text={item.git_ref === item.version
                ? item.version.slice(0, 7)
                : (item.git_ref.length <= 16
                    ? item.git_ref
                    : `${item.git_ref.slice(0, 16)}...`) +
                  `@${item.version.slice(0, 7)}`}
            />
          </Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.status.name}
                src={mapImage("job_status", item.status.name, "svg")}
                class={getStatusStyle(item)}
              />
              <Tooltip>{item.status.name}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell class="md">
            <Wrapper>
              <span>
                <div>{calculateElapsed(item)}</div>
                <div>{calculateAge(item)}</div>
              </span>
              <Tooltip>{readableDateTime(item.created_at)}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell class="lg">
            <Wrapper>
              <span class="table-text worker-version"
                >{item.worker_version || "(pending)"}</span
              >
              <Tooltip>{item.worker_version || "(pending)"}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.user.name}
                src={item.user.avatar_url}
                style="max-height: 40px;"
              />
              <Tooltip>{item.user.name}</Tooltip>
            </Wrapper>
          </Cell>
          <!-- <Cell>
            {#if true}
              <img
                alt={"approved"}
                src={"/icons/job_status/approved.svg"}
                style="max-height: 30px;"
              />
            {/if}
            <Wrapper>
              <Tooltip>{item.user.name}</Tooltip>
            </Wrapper>
          </Cell> -->
        </Row>
      {/each}
    </Body>
    <Pagination slot="paginate">
      <svelte:fragment slot="rowsPerPage">
        <Label>Rows Per Page</Label>
        <Select variant="outlined" bind:value={rowsPerPage} noLabel>
          <Option value={10}>10</Option>
          <Option value={25}>25</Option>
          <Option value={100}>100</Option>
        </Select>
      </svelte:fragment>
      <svelte:fragment slot="total">
        {start + 1}-{end} of {sortedRows.length}
      </svelte:fragment>

      <IconButton
        class="material-icons"
        action="first-page"
        title="First page"
        on:click={() => (currentPage = 0)}
        disabled={currentPage === 0}>first_page</IconButton
      >
      <IconButton
        class="material-icons"
        action="prev-page"
        title="Prev page"
        on:click={() => currentPage--}
        disabled={currentPage === 0}>chevron_left</IconButton
      >
      <IconButton
        class="material-icons"
        action="next-page"
        title="Next page"
        on:click={() => currentPage++}
        disabled={currentPage === lastPage}>chevron_right</IconButton
      >
      <IconButton
        class="material-icons"
        action="last-page"
        title="Last page"
        on:click={() => (currentPage = lastPage)}
        disabled={currentPage === lastPage}>last_page</IconButton
      >
    </Pagination>
  </DataTable>

  <DetailsDialog bind:open={detailsOpen} {selectedJob} {config} />
  <ApprovedBooksDialog bind:open={ablOpen} />
</div>

<style>
  @keyframes spin-frames {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  @keyframes bounce-frames {
    0% {
      transform: translateY(5px) rotate(0deg);
    }
    25% {
      transform: translateY(0px) rotate(-5deg);
    }
    50% {
      transform: translateY(5px) rotate(0deg);
    }
    75% {
      transform: translateY(0px) rotate(5deg);
    }
    100% {
      transform: translateY(5px) rotate(0deg);
    }
  }

  @keyframes rock-frames {
    0% {
      transform: translateX(0px) rotate(0deg);
    }
    25% {
      transform: translateX(-10px) rotate(-25deg);
    }
    50% {
      transform: translateX(0px) rotate(0deg);
    }
    75% {
      transform: translateX(10px) rotate(25deg);
    }
    100% {
      transform: translateX(0px) rotate(0deg);
    }
  }

  @keyframes pulse-frames {
    50% {
      transform: scale(0.9);
    }
  }

  :global(.abl) {
    background-color: rgba(0, 255, 128, 0.2) !important;
  }

  .job-status-icon {
    max-height: 40px;
  }

  .spin {
    animation-name: spin-frames;
    animation-duration: 1.5s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
  }

  .bounce {
    animation-name: bounce-frames;
    animation-duration: 1.5s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
  }

  .rock {
    animation-name: rock-frames;
    animation-duration: 1.5s;
    animation-iteration-count: infinite;
    animation-timing-function: linear;
  }

  .pulse {
    animation-name: pulse-frames;
    animation-duration: 1.5s;
    animation-iteration-count: 2;
    animation-timing-function: linear;
  }

  :global(#repo-input > div > label, #book-input > div > label) {
    width: 280px !important;
  }

  :global(#version-input > div > label) {
    width: 120px !important;
  }

  .job-type-icon {
    max-height: 40px;
  }

  .job-type-icon[data-is-complete="false"] {
    opacity: 0.5;
    filter: grayscale(1);
  }

  .table-text {
    display: inline-block;
    vertical-align: middle;
    overflow-x: hidden;
    text-overflow: ellipsis;
  }

  .table-text.book,
  .table-text.repo {
    max-width: 250px;
  }

  .table-text.worker-version {
    max-width: 150px;
  }

  @media (max-width: 1000px) {
    :global(.lg) {
      display: none;
    }
  }

  @media (max-width: 800px) {
    :global(.md) {
      display: none;
    }
  }
</style>
