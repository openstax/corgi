<div class="columns margins">
    <Autocomplete
    options={columns.includes(filterValue) ? ['PDF', 'Web Preview'] : options}
    bind:value={filterValue}
    label="Filter"
    />
    <pre class="status">Selected: {filterValue || ''}</pre>
</div>
  
<Button on:click={addInputChip}><Label>Filter</Label></Button>
<Set chips={filters} let:chip input>
    <Chip {chip}>
        <Text>{chip}</Text>
        <TrailingAction icon$class="material-icons">cancel</TrailingAction>
    </Chip>
</Set>
  
<script lang="ts">
    import Autocomplete from '@smui-extra/autocomplete';
    import Chip, { Set, TrailingAction, Text } from '@smui/chips';
    import Button, { Label } from '@smui/button';

    let columns = ['JobId', 'JobType', 'Repo', 'Version', 'StartTime', 'UpdateTime', 'DownloadUrl', 'Status', 'WorkerVersion'];

    let options = columns

    let filterValue: string | undefined = undefined;

    let filters = [];
  
    function addInputChip() {
        filters.push(filterValue);
        filters = filters;
    }
  </script>
  