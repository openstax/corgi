<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px; padding-top: 8px;"
/>

<NewJobForm 
  bind:selectedJobTypes
  bind:selectedRepo
  bind:selectedBook
  clickNewJob={clickNewJob} 
/>

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
        <Cell columnId="job_type" style="width: 100%;">
          <Label>Type</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="repository" style="width: 100%;">
          <Label>Repo</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="books" style="width: 100%;">
          <Label>Book</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="version" style="width: 100%;">
          <Label>Version</Label>
          <IconButton class="material-icons">arrow_upward</IconButton>
        </Cell>
        <Cell columnId="status" style="width: 100%;" sortable={false}>
          <Label>Status</Label>
        </Cell>
        <Cell columnId="updated-at" style="width: 100%;" sortable={false}>
          <Label>Elapsed</Label>
        </Cell>
        <Cell columnId="github-user" style="width: 100%;" sortable={false}>
          <Label>User</Label>
        </Cell>
        <!-- <Cell columnId="approved" style="width: 100%;" sortable={false}>
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
        <Row slot="data">
          <Cell numeric>
            <Button
              on:click={() => {
                selectedJob = item
                open = true
              }}
            >
              {item.id}
            </Button>
          </Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.job_type.display_name}
                src={mapImage('job_type', item.job_type.display_name, 'svg')}
                style="max-height: 40px;"
              />
              <Tooltip>{item.job_type.display_name}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell>
            {repoToString(item.repository)}
          </Cell>
          <Cell>
            {#if item.books.length === 1}
              {item.books[0].slug}
            {:else}
              <Wrapper>
                <span>all</span>
                <Tooltip>
                  {#each item.books as book}
                    {book.slug}<br />
                  {/each}
                </Tooltip>
              </Wrapper>
            {/if}
          </Cell>
          <Cell>
            {item.version === null ? "main" : item.version.slice(0, 7)}
          </Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.status.name}
                src={mapImage("job_status", item.status.name, "svg")}
                class={statusStyles[item.status.name]}
              />
              <!-- style="max-height: 30px; color: greenyellow" -->
              <Tooltip>{item.status.name}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell>
            <Wrapper>
              <span>{calculateElapsed(item)}</span>
              <Tooltip>{readableDateTime(item.created_at)}</Tooltip>
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
        {start + 1}-{end} of {jobs.length}
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

  <DetailsDialog bind:open {selectedJob} />
</div>

<script lang="ts">
  import Tooltip, { Wrapper } from "@smui/tooltip";
  import {
    calculateElapsed,
    mapImage,
    handleError,
    repoToString,
    readableDateTime
  } from "../ts/utils";
  import NewJobForm from "./NewJobForm.svelte";
  import { submitNewJob, getJobs } from "../ts/jobs";
  import type { Repository } from "../ts/types";
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
  import { repoSummariesStore, jobsStore } from "../ts/stores";

  import type { Job, JobType } from "../ts/types";
  import DetailsDialog from "./DetailsDialog.svelte";
  import { SECONDS } from "../ts/time";

  let statusStyles = {
    queued: "filter-yellow rock",
    assigned: "filter-yellow rock",
    processing: "filter-yellow rock",
    failed: "filter-red",
    completed: "filter-green bounce",
    aborted: "filter-red",
  };

  let selectedJobTypes = [];

  let open = false;
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
    selectedJobTypes
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
          selectedVersion
        );
      })
    );
    setTimeout(async () => {
      await Promise.all([
        jobsStore.update(),
        repoSummariesStore.update()
      ])
    }, 1 * SECONDS);
  }

  // Pagination
  let rowsPerPage = 10;
  let currentPage = 0;
  $: start = currentPage * rowsPerPage;
  $: end = Math.min(start + rowsPerPage, jobs.length);
  $: lastPage = Math.max(Math.ceil(jobs.length / rowsPerPage) - 1, 0);
  $: if (currentPage > lastPage) {
    currentPage = lastPage;
  }

  // Job filtering
  $: filteredRows = jobs.filter(
    (entry) =>
      (selectedJobTypes.length === 0 ||
        selectedJobTypes.some((id) =>
          entry.job_type.display_name.includes(id)
        )) &&
      (!selectedRepo ||
        repoToString(entry.repository).includes(selectedRepo)) &&
      (!selectedBook ||
        entry.books.find((item) => item.slug.includes(selectedBook)) != null)
  );

  // Job sorting
  $: sortedRows = filteredRows.sort((a, b) => {
    let [aVal, bVal] = [a[sort], b[sort]][
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
    } else if (aVal instanceof Array && bVal instanceof Array) {
      // lexicographic string sort for books
      let a: string[];
      let b: string[];
      if (sort === "books") {
        a = aVal.map((b) => b.slug);
        b = bVal.map((b) => b.slug);
      } else {
        handleError(new Error(`Cannot handle list sort of ${sort}`));
        return;
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
    jobsStore.subscribe(updatedJobs => jobs = updatedJobs)
    await jobsStore.update()
    jobsStore.startPolling(10 * SECONDS)
  });
</script>

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
    0%{transform:translateY(5px) rotate(0deg)}
    25%{transform:translateY(0px) rotate(-5deg)}
    50%{transform:translateY(5px) rotate(0deg)}
    75%{transform:translateY(0px) rotate(5deg)}
    100%{transform:translateY(5px) rotate(0deg)} 
  }

  @keyframes rock-frames {
    0%{transform:translateX(0px) rotate(0deg)}
    25%{transform:translateX(-10px) rotate(-25deg)}
    50%{transform:translateX(0px) rotate(0deg)}
    75%{transform:translateX(10px) rotate(25deg)}
    100%{transform:translateX(0px) rotate(0deg)} 
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

  :global(#repo-input > div > label, #book-input > div > label) {
    width: 280px !important;
  }

  :global(#version-input > div > label) {
    width: 120px !important;
  }
</style>
