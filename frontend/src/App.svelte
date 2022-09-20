<!-- <NewJobForm bind:selected={selected}></NewJobForm> -->
<JobsTable></JobsTable>
<!-- <JobsTable bind:selected={selected}></JobsTable> -->
<!-- <AutoAdjust {topAppBar}>  
</AutoAdjust> -->

 
<script lang="ts">
  import NewJobForm from './NewJobForm.svelte';
  import JobsFilter from './JobsFilter.svelte';
  import JobsTable from './JobsTable.svelte';
  import type { TopAppBarComponentDev } from '@smui/top-app-bar';
  import TopAppBar, { Row, Section, Title, AutoAdjust } from '@smui/top-app-bar';
  import IconButton from '@smui/icon-button';

  let topAppBar: TopAppBarComponentDev;

  let selected:string[];

</script>
