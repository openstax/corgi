<img
  alt="Content Output Review and Generation Interface"
  src="./title-image.png"
  style="max-height: 100px;"
/>

<div class="inputContainer">
  <Autocomplete
  id="repo-input"
  type="email"
  options={repos}
  bind:text={repo}
  updateInvalid
  label="Repo"
  />

  <Autocomplete
  id="book-input"
  options={books}
  bind:text={book}
  label="Book"
  />

  <Autocomplete
  id="version-input"
  options={versions}
  bind:text={version}
  label="Version"
  />
</div>

<div class="inputContainer">
{#each options as option}
  <FormField>
    <Checkbox
      id={`${option.name}-job-option`}
      bind:group={selected}
      value={option.name}
      disabled={option.disabled}
    />
    <span slot="label">{option.name}{option.disabled ? ' (disabled)' : ''}</span>
  </FormField>
{/each}
</div>

<Button id="submit-job-button" disabled={!validJob} on:click={clickNewJob}>
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
      <Cell columnId="created_at" style="width: 100%;">
        <Label>Started</Label>
        <IconButton class="material-icons">arrow_upward</IconButton>
      </Cell>
      <Cell columnId="updated-at" style="width: 100%;" sortable={false}>
        <Label>Elapsed</Label>
      </Cell>
      <Cell columnId="github-user" style="width: 100%;" sortable={false}>
        <Label>User</Label>
      </Cell>
    </Row>
  </Head>
  <Body>
    {#each sortedRows as item (item.id)}
      <DetailRow>
        <Row slot="data">
        <Cell numeric class="responsiveCell">{item.id}</Cell>
        <Cell class="responsiveCell">
          <img
            alt={item.job_type.display_name}
            src={mapImage(item.job_type.display_name)}
            style="max-height: 100px;"
          />
        </Cell>
        <Cell class="responsiveCell">{item.book}</Cell>
        <Cell class="responsiveCell">{item.repo}</Cell>
        <Cell class="responsiveCell">{item.version === null ? 'main' : item.version }</Cell>
        <Cell class="responsiveCell">
          <img
            alt={item.status.name}
            src={mapImage(item.status.name)}
            style="max-height: 100px;"
          />
        </Cell>
        <Cell class="responsiveCell">{item.created_at}</Cell>
        <Cell class="responsiveCell">{item.elapsed}</Cell>
        <Cell class="responsiveCell">username</Cell>
        </Row>
        <Row slot="detail">
          <Cell colspan=8>{item.book}</Cell>
        </Row>
      </DetailRow>
      <!-- where does details Accordion go? -->
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
  import DetailRow from './DetailRow.svelte'
  import { mapImage, readableDateTime } from './ts/utils'
  import { repos, books, fetchRepos, fetchBooks, fetchVersions } from './ts/data'
  import { submitNewJob, getJobsForPage } from './ts/jobs'
  let versions = [];
  

  import { onMount } from 'svelte';
  // import LayoutGrid, { Cell } from '@smui/layout-grid';
  import Checkbox from '@smui/checkbox';
  import FormField from '@smui/form-field';
  import Autocomplete from '@smui-extra/autocomplete';
  // import Button, { Label } from '@smui/button';
  import Button from '@smui/button';
  // import {filteredRows} from './stores.js'
  
  let options = [
    { name: 'PDF',     disabled: false },
    { name: 'WebView', disabled: false },
    { name: 'EPUB',    disabled: false },
    { name: 'Docx',    disabled: false },
  ];

  export let selected = [];
  
  let repo: string | undefined = undefined;
  let book: string | undefined = undefined;
  let version: string | undefined = undefined;

  $: validJob = (selected.length != 0) && (repo !== '');
  
  // Initialization
  import CircularProgress from '@smui/circular-progress';
  import DataTable, {
    Head,
    Body,
    Row,
    Cell,
    SortValue,
    Pagination
  } from '@smui/data-table';
  import Select, { Option } from '@smui/select';
  import IconButton from '@smui/icon-button';
  import Accordion, { Panel, Header, Content } from '@smui-extra/accordion';
  import { Label } from '@smui/common';
  import { writable, derived } from 'svelte/store';

  import type { Job } from './ts/types';

  let jobs: Job[] = [];
  let sort: keyof Job = 'id';
  let sortDirection: Lowercase<keyof typeof SortValue> = 'ascending';

  onMount(async () => {
    jobs = await getJobsForPage(currentPage, rowsPerPage);
    await fetchRepos();
    await fetchBooks();
    await fetchVersions();
    pollData();
	});

  if (typeof fetch !== 'undefined') {
    // 'https://corgi.ce.openstax.org/api/jobs'
    fetch(
      '/home/jobs.json'
    )
    .then((response) => response.json())
    .then((json) => {
      jobs = json.map((entry) => {
        // split collection id to repo and book
        const index = entry.collection_id.lastIndexOf('/');
        entry.repo = entry.collection_id.slice(0, index);
        entry.book = entry.collection_id.slice(index + 1);

        // format timestamps
        entry.created_at = readableDateTime(entry.created_at);
        let start_time = new Date(entry.created_at);
        let update_time = new Date(entry.updated_at);
        let elapsed = update_time.getTime() - start_time.getTime();
        entry.elapsed = new Date(elapsed * 1000).toISOString().substring(11, 16)

        return entry; 
      })
      slice = jobs.slice(start, end);
    });
  }

  // Job creation
  function clickNewJob() {
    if (lastJobStartTime + jobStartRateLimitDurationMillis > Date.now()) {
      return
    }
    lastJobStartTime = Date.now()
    // submitNewJob();
  }
  
  const jobStartRateLimitDurationMillis = 1000;
  let lastJobStartTime = Date.now();

  // Job polling
  let polling;

  function pollData () {
    polling = setInterval(
      async () => { await getJobsForPage(currentPage, rowsPerPage) }, 
      30000
    )
  }

  // Pagination
  let rowsPerPage = 10;
  let currentPage = 0;

  $: start = currentPage * rowsPerPage;
  $: end = Math.min(start + rowsPerPage, jobs.length);
  $: slice = jobs.slice(start, end);
  $: lastPage = Math.max(Math.ceil(jobs.length / rowsPerPage) - 1, 0);
  $: if (currentPage > lastPage) {
    currentPage = lastPage;
  }

  // Job filtering
  $: filteredRows = slice.filter(entry => 
    (selected.length === 0 || selected.some(item => entry.job_type.display_name.includes(item))) && 
    (repo == undefined || entry.repo.includes(repo)) &&
    (book == undefined || entry.repo.includes(book))
  )

  // Job sorting
  $: sortedRows = filteredRows.sort((a, b) => {
    console.log(sort)
    console.log([a[sort], b[sort]])
    let [aVal, bVal] = [a[sort], b[sort]][
      sortDirection === 'ascending' ? 'slice' : 'reverse'
    ]();
    if (sort === 'job_type') {
      aVal = (aVal as any).display_name
      bVal = (bVal as any).display_name
    }
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return aVal.localeCompare(bVal);
    }
    return Number(aVal) - Number(bVal);
  })
</script>

<style>
  /* Not fully implemented yet
  .responsiveCell {
    display: flex;
    align-items: center;
    justify-content: space-between;
  } */
</style>