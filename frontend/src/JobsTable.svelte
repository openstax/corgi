<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px;"
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
      value={option.name}
      disabled={option.disabled}
    />
    <span slot="label">{option.name}{option.disabled ? ' (disabled)' : ''}</span>
  </FormField>
{/each}
</div>

<Button id="submit-job-button" variant="raised" color="secondary" disabled={!validJob} on:click={clickNewJob}>
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
      <Cell columnId="collection_id" style="width: 100%;">
        <Label>Book</Label>
        <IconButton class="material-icons">arrow_upward</IconButton>
      </Cell>
      <Cell columnId="collection-id" style="width: 100%;">
        <Label>Repo</Label>
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
        <Row slot="data" on:click={() => {selectedJob=item; open=true}}>
          <Cell numeric >{item.id}</Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.job_type.display_name}
                src={mapImage('job_type', item.job_type.display_name, 'png')}
                style="max-height: 100px;"
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
                    {book.slug}<br>
                  {/each}
                </Tooltip>
              </Wrapper>
            {/if}
          </Cell>
          <Cell>
            {#if item.repository.owner != "openstax"}
              {item.repository.owner}/
            {/if}
            {item.repository.name}
          </Cell>
          <Cell>{item.version === null ? 'main' : item.version.slice(0, 7) }</Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.status.name}
                src={mapImage('job_status', item.status.name, 'svg')}
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

<DetailsDialog bind:open={open} selectedJob={selectedJob}></DetailsDialog>
</div>

<script lang="ts">
  import Tooltip, { Wrapper } from '@smui/tooltip'
  import { fetchRepos as fetchRepos, calculateElapsed, mapImage, filterBooks } from './ts/utils'
  import { submitNewJob, getJobs, repeatJob } from './ts/jobs'
  import Dialog, { Header, Title, Content, Actions, InitialFocus } from '@smui/dialog'
  import LinearProgress from '@smui/linear-progress'
  import type { Repository, RepositorySummary } from './ts/types'
  import { onMount } from 'svelte'
  import Checkbox from '@smui/checkbox'
  import FormField from '@smui/form-field'
  import Autocomplete from '@smui-extra/autocomplete'
  import Button from '@smui/button'
  import CircularProgress from '@smui/circular-progress'
  import DataTable, {
    Head,
    Body,
    Row,
    Cell,
    SortValue,
    Pagination
  } from '@smui/data-table'
  import Select, { Option } from '@smui/select'
  import IconButton from '@smui/icon-button'
  import { Label } from '@smui/common'

  import type { Job, JobType } from './ts/types'
  import DetailsDialog from './DetailsDialog.svelte';

  let options = [
    { name: 'PDF',     disabled: false },
    { name: 'WebView', disabled: false },
    { name: 'EPUB',    disabled: false },
    { name: 'Docx',    disabled: false },
  ]

  let statusColors = {
    queued: "filter-yellow",
    assigned: "filter-yellow",
    processing: "filter-yellow spin",
    failed: "filter-red",
    completed: "filter-green",
    aborted: "filter-red"
  }

  let repos: RepositorySummary[] = []
  let versions: string[] = []

  export let selectedJobTypes = []

  let open = false
  let selectedJob: Job
  
  let selectedRepo: string
  let selectedBook: string
  let selectedVersion: string

  $: validJob = (selectedJobTypes.length != 0) && (selectedRepo !== '')
  
  // Initialization
  let jobs: Job[] = []
  let slice: Job[] = []
  let sort: keyof Job = 'id'
  let sortDirection: Lowercase<keyof typeof SortValue> = 'ascending'

  enum JobTypeId {
    PDF = 3,
    WebView = 4,
    Docx = 5,
    EPUB = 6
  }

  // Job creation
  async function clickNewJob() {
    if (lastJobStartTime + jobStartRateLimitDurationMillis > Date.now()) {
      return
    }
    lastJobStartTime = Date.now()
    selectedJobTypes.forEach(jobType => {
      submitNewJob(JobTypeId[(jobType as number)], selectedRepo, selectedBook, selectedVersion)
    })
    jobs = await getJobs()
  }
  
  const jobStartRateLimitDurationMillis = 1000
  let lastJobStartTime = Date.now()

  let polling; 

  // Job polling
  function pollData () {
    polling = setInterval(
      async () => { jobs = await getJobs() }, 
      10000
    )
  }

  // Pagination
  let rowsPerPage = 10
  let currentPage = 0
  $: start = currentPage * rowsPerPage
  $: end = Math.min(start + rowsPerPage, jobs.length)
  $: { slice = jobs.slice(start, end);}
  $: lastPage = Math.max(Math.ceil(jobs.length / rowsPerPage) - 1, 0)
  $: if (currentPage > lastPage) {
    currentPage = lastPage
  }

  // Job filtering
  
  let repoSummaries: RepositorySummary[] | null = null
  
  async function getRepoSummaries() {
    if (repoSummaries === null) {
      repoSummaries = await fetchRepos()
    }
    return repoSummaries
  }
  
  async function searchRepos(input: string) {
    const fullOptions = await getRepoSummaries()
    const lowerInput = input.toLocaleLowerCase()
    
    const repos = fullOptions.map(r => r.name).filter(name =>
      name.toLocaleLowerCase().includes(input)
    )

    return repos
  }

  async function searchBooks(input: string) {
    // Does not filter by repo until you type at least one character
    // Does not reset until you type at least one char
    // Locks value of repo once book is selected to repo that book belongs to
    return filterBooks(await getRepoSummaries(), selectedRepo).filter(b => b.toLocaleLowerCase().includes(input.toLocaleLowerCase()))
  }
  
/*
  
*/

  $: repoNames = repos.map(m => m.name)
  // $: books = repos.length > 0 ? filterBooks(repos, selected_repo) : []
  $: books = repos.length > 0 ? filterBooks(repos, selectedRepo) : []

  function setSelectedRepo(selectedBook) {
    return repos.find(r => r.books.find(b => b === selectedBook))?.name || selectedRepo
  }

  $: selectedRepo = setSelectedRepo(selectedBook)
  $: filteredRows = slice.filter(entry =>
      (selectedJobTypes.length === 0 || selectedJobTypes.some(item => entry.job_type.display_name.includes(item))) && 
      (!selectedRepo || entry.repository.name.includes(selectedRepo)) &&
      (!selectedBook || entry.books.find(item => item.slug.includes(selectedBook)) != null)
    )

  // Job sorting
  $: sortedRows = filteredRows.sort((a, b) => {
    let [aVal, bVal] = [a[sort], b[sort]][
      sortDirection === 'ascending' ? 'slice' : 'reverse'
    ]()
    if (sort === 'job_type') {
      aVal = (aVal as any).display_name
      bVal = (bVal as any).display_name
    }
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return aVal.localeCompare(bVal)
    }
    return Number(aVal) - Number(bVal)
  })

  onMount(async () => {
    repos = await fetchRepos()
    jobs = await getJobs()
    pollData()
	})
</script>

<style>
  .filter-green {
    filter: invert(48%) sepia(79%) saturate(200%) hue-rotate(77deg) brightness(118%) contrast(119%);
  }
  .filter-yellow {
    filter: invert(48%) sepia(79%) saturate(240%) hue-rotate(5deg) brightness(145%) contrast(119%);
  }
  .filter-red {
    filter: invert(48%) sepia(79%) saturate(500%) hue-rotate(-50deg) brightness(118%) contrast(119%);
  }
  @keyframes spin-frames {
    0% { transform:rotate(0deg) }
    100% { transform:rotate(360deg) }
  }
  .spin {
    animation-name: spin-frames;
    animation-duration: 1.5s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
  }
</style>
  
  