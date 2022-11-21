<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px; padding-top: 8px;"
/>

<div class="inputContainer">
  <Autocomplete
    id="repo-input"
    type="email"
    search={searchRepos}
    bind:text={selectedRepo}
    updateInvalid
    label="Repo"
  />

  <Autocomplete
    id="book-input"
    search={searchBooks}
    options={books}
    bind:text={selectedBook}
    label="Book"
  />

  <Autocomplete
    id="version-input"
    search={searchVersions}
    options={versions}
    bind:text={selectedVersion}
    label="Version"
  />
</div>

<div class="inputContainer">
  {#each options as option}
    <FormField>
      <Checkbox
        id={`${option.name}-job-option`}
        bind:group={selectedJobTypes}
        value={option.id}
        disabled={option.disabled}
      />
      <span slot="label"
        >{option.name}{option.disabled ? " (disabled)" : ""}</span
      >
    </FormField>
  {/each}
</div>

<Button
  id="submit-job-button"
  variant="raised"
  color="secondary"
  disabled={!validJob}
  on:click={clickNewJob}
>
  <Label>Create New Job</Label>
</Button>

<!--NewJobForm ends here-->

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
      {#each sortedRows as item (item.id)}
        <!-- <DetailRow> -->
        <Row
          slot="data"
          on:click={() => {
            selectedJob = item;
            open = true;
          }}
        >
          <Cell numeric>{item.id}</Cell>
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
            {repoToString(item.repository)}
          </Cell>
          <Cell
            >{item.version === null ? "main" : item.version.slice(0, 7)}</Cell
          >
          <Cell>
            <Wrapper>
              <img
                alt={item.status.name}
                src={mapImage("job_status", item.status.name, "svg")}
                class={statusColors[item.status.name]}
              />
              <!-- style="max-height: 30px; color: greenyellow" -->
              <Tooltip>{item.status.name}</Tooltip>
            </Wrapper>
          </Cell>
          <Cell>
            <Wrapper>
              <span>{calculateElapsed(item)}</span>
              <Tooltip>{item.created_at}</Tooltip>
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
    fetchRepoSummaries,
    calculateElapsed,
    mapImage,
    filterBooks,
    handleError,
    repoToString,
  } from "./ts/utils";
  import { submitNewJob, getJobs } from "./ts/jobs";
  import type { Book, Repository, RepositorySummary, Status } from "./ts/types";
  import { onMount } from "svelte";
  import Checkbox from "@smui/checkbox";
  import FormField from "@smui/form-field";
  import Autocomplete from "@smui-extra/autocomplete";
  import Button from "@smui/button";
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

  import type { Job, JobType } from "./ts/types";
  import DetailsDialog from "./DetailsDialog.svelte";

  let options = [
    { name: "PDF", id: "PDF", disabled: false },
    { name: "WebView", id: "Web", disabled: false },
    { name: "EPUB", id: "EPUB", disabled: true },
    { name: "Docx", id: "Docx", disabled: false },
  ];

  let statusColors = {
    queued: "filter-yellow",
    assigned: "filter-yellow",
    processing: "filter-yellow spin",
    failed: "filter-red",
    completed: "filter-green",
    aborted: "filter-red",
  };

  let repos: RepositorySummary[] = [];
  let versions: string[] = [];

  export let selectedJobTypes = [];

  let open = false;
  let selectedJob: Job;

  let selectedRepo: string;
  let selectedBook: string;
  let selectedVersion: string;

  $: validJob = selectedJobTypes.length != 0 && selectedRepo !== "" && selectedBook !== "";

  // Initialization
  let jobs: Job[] = [];
  let slice: Job[] = [];
  let sort: keyof Job = "id";
  let sortDirection: Lowercase<keyof typeof SortValue> = "descending";

  enum JobTypeId {
    PDF = 3,
    WebView = 4,
    Docx = 5,
    EPUB = 6,
  }

  // Job creation
  async function clickNewJob() {
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
      jobs = await getJobs();
    }, 1000);
  }

  const jobStartRateLimitDurationMillis = 1000;
  let lastJobStartTime = Date.now();

  let polling;

  // Job polling
  function pollData() {
    polling = setInterval(async () => {
      jobs = await getJobs();
    }, 10000);
  }

  // Pagination
  let rowsPerPage = 10;
  let currentPage = 0;
  $: start = currentPage * rowsPerPage;
  $: end = Math.min(start + rowsPerPage, jobs.length);
  $: {
    slice = jobs.slice(start, end);
  }
  $: lastPage = Math.max(Math.ceil(jobs.length / rowsPerPage) - 1, 0);
  $: if (currentPage > lastPage) {
    currentPage = lastPage;
  }

  // Job filtering

  // let repoSummaries: RepositorySummary[] = []

  async function getRepoSummaries() {
    if (repos.length === 0) {
      repos = await fetchRepoSummaries();
    }
    return repos;
  }

  function createSearchFunction(
    getOptions: (
      repoSummaries: RepositorySummary[],
      lowerInput: string
    ) => string[]
  ) {
    return async function (input: string) {
      try {
        const repoSummaries = await getRepoSummaries();
        const lowerInput = input.toLocaleLowerCase().trim();
        const options = getOptions(repoSummaries, lowerInput);
        if (lowerInput) {
          const trimmedInput = input.trim();
          if (options.length > 1 || options.indexOf(trimmedInput) === -1) {
            options.push(trimmedInput);
          }
        }
        return options;
      } catch (e) {
        handleError(e);
      }
    };
  }

  const searchRepos = createSearchFunction((repoSummaries, lowerInput) => {
    if (!!selectedBook) {
      repoSummaries = repoSummaries.filter((repo) =>
        repo.books.includes(selectedBook)
      );
    }
    return repoSummaries
      .map((repo) => repoToString(repo))
      .filter((repoPath) => repoPath.toLocaleLowerCase().includes(lowerInput));
  });

  const searchBooks = createSearchFunction((repoSummaries, lowerInput) =>
    filterBooks(repoSummaries, selectedRepo).filter((bookSlug) =>
      bookSlug.toLocaleLowerCase().includes(lowerInput)
    )
  );

  const searchVersions = createSearchFunction(
    (_repoSummaries, _lowerInput) => []
  );

  /*
  
*/

  $: books = repos.length > 0 ? filterBooks(repos, selectedRepo) : [];

  function setSelectedRepo(selectedBook) {
    const repo = repos.find((r) => r.books.find((b) => b === selectedBook));
    return !!repo ? repoToString(repo) : selectedRepo;
  }

  $: selectedRepo = setSelectedRepo(selectedBook);
  $: filteredRows = slice.filter(
    (entry) =>
      (selectedJobTypes.length === 0 ||
        selectedJobTypes.some((item) =>
          entry.job_type.display_name.includes(item)
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

  onMount(async () => {
    repos = await fetchRepoSummaries();
    jobs = await getJobs();
    pollData();
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
  .spin {
    animation-name: spin-frames;
    animation-duration: 1.5s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
  }

  :global(#repo-input > div > label, #book-input > div > label) {
    width: 280px !important;
  }

  :global(#version-input > div > label) {
    width: 120px !important;
  }
</style>
