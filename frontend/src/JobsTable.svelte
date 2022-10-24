<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px;"
/>

<div class="inputContainer">
  <Autocomplete
  id="repo-input"
  type="email"
  options={repoNames}
  bind:text={selected_repo}
  updateInvalid
  label="Repo"
  />

  <Autocomplete
  id="book-input"
  search={searchBooks}
  options={books}
  bind:text={selected_book}
  label="Book"
  />

  <Autocomplete
  id="version-input"
  options={versions}
  bind:text={selected_version}
  label="Version"
  />
</div>

<div class="inputContainer">
{#each options as option}
  <FormField>
    <Checkbox
      id={`${option.name}-job-option`}
      bind:group={selected_job_types}
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
        <Row slot="data" on:click={() => {open=true}}>
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
          <Cell>{item.version === null ? 'main' : item.version }</Cell>
          <Cell>
            <Wrapper>
              <img
                alt={item.status.name}
                src={mapImage('job_status', item.status.name, 'svg')}
                class="filter-green"
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
        <Dialog
          bind:open
        >

          {#if item.status.name == "completed"}
            <Title>Job Actions</Title>
            <Actions>
              <Button variant="raised" on:click={() => {repeatJob(item)}}>
                <Label>Repeat</Label>
                </Button>
              <Button color="secondary" variant="raised" on:click={clickNewJob}>
                <Label>Approve</Label>
              </Button>
            </Actions>
          {:else if item.status.name == "queued"}
            <Title>Job Actions</Title>
            <Actions>
              <Button variant="raised" on:click={clickNewJob}>
                <Label>Abort</Label>
              </Button>
            </Actions>
          {:else if item.status.name == "failed"}
            <Title>Errors</Title>
            <Content>
            </Content>
          {/if}
        </Dialog>
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
</div>

<script lang="ts">
  import Tooltip, { Wrapper } from '@smui/tooltip'
  import { fetchRepos as fetchRepos, calculateElapsed, mapImage, filterBooks } from './ts/utils'
  import { submitNewJob, getJobs, repeatJob } from './ts/jobs'
  import Dialog, { Header, Title, Content, Actions } from '@smui/dialog'
  import LinearProgress from '@smui/linear-progress'
  import type { Repository, RepositorySummary } from './ts/types'



  import { onMount } from 'svelte'
  import Checkbox from '@smui/checkbox'
  import FormField from '@smui/form-field'
  import Autocomplete from '@smui-extra/autocomplete'
  import Button from '@smui/button'
  
  let options = [
    { name: 'PDF',     disabled: false },
    { name: 'WebView', disabled: false },
    { name: 'EPUB',    disabled: false },
    { name: 'Docx',    disabled: false },
  ]

  let repos: RepositorySummary[] = []
  let versions: string[] = []
  
  let open = false

  export let selected_job_types = []
  
  let selected_repo: string
  let selected_book: string
  let selected_version: string

  $: validJob = (selected_job_types.length != 0) && (selected_repo !== '')
  
  // Initialization
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

  let jobs: Job[] = []
  let slice: Job[] = []
  let sort: keyof Job = 'id'
  let sortDirection: Lowercase<keyof typeof SortValue> = 'ascending'

  onMount(async () => {
    repos = await fetchRepos()
    jobs = await getJobs()
    pollData()
	})

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
    selected_job_types.forEach(jobType => {
      submitNewJob(JobTypeId[(jobType as number)], selected_repo, selected_book, selected_version)
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

  async function searchBooks(input: string) { 
    // Pretend to have some sort of canceling mechanism.
    // const myCounter = ++counter
 
    // // Pretend to be loading something...
    // await new Promise((resolve) => setTimeout(resolve, 1000))
 
    // // This means the function was called again, so we should cancel.
    // if (myCounter !== counter) {
    //   // `return false` (or, more accurately, resolving the Promise object to
    //   // `false`) is how you tell Autocomplete to cancel this search. It won't
    //   // replace the results of any subsequent search that has already finished.
    //   return false
    // }
 
    // // Return a list of matches.
    // return fruits.filter((item) =>
    //   item.toLowerCase().includes(input.toLowerCase())
    // )

    return filterBooks(repos, selected_repo)
  }

  
  $: repoNames = repos.length > 0 ? repos.map(m => m.name) : []
  // $: books = repos.length > 0 ? filterBooks(repos, selected_repo) : []
  $: books = repos.length > 0 ? repos.map(r => r.books).reduce((ax=[], x) => ax.concat(x)) : []

  $: selected_repo = repos.find(r => r.books.find(b => b === selected_book))?.name || selected_repo
  $: filteredRows = slice.filter(entry =>
      (selected_job_types.length === 0 || selected_job_types.some(item => entry.job_type.display_name.includes(item))) && 
      (!selected_repo || entry.repository.name.includes(selected_repo)) &&
      (!selected_book || entry.books.find(item => item.slug.includes(selected_book)) != null)
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
</script>

<style>
  .filter-green {
    filter: invert(48%) sepia(79%) saturate(200%) hue-rotate(77deg) brightness(118%) contrast(119%);
  }
</style>
  
  