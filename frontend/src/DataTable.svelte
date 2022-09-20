<table>
    <DataHead>
        <tr>
            {#each cols as col}
                <DataCell>{col}</DataCell>
            {/each}
        </tr>
    </DataHead>
    <DataBody>
      {#each rows as row}
        <DataRow>
            {#each Object.entries(row) as [key, val] (key)}
                <DataCell>{val}</DataCell>
            {/each}
        </DataRow>
      {/each}
    </DataBody>
    <DataFoot>
    </DataFoot>
</table>

<script lang="ts">
    import DataHead from './DataHead.svelte'
    import DataBody from './DataBody.svelte'
    import DataFoot from './DataFoot.svelte'
    import DataRow from './DataRow.svelte'
    import DataCell from './DataCell.svelte'
    type Job = {
        thing1: string;
        thing2: number;
        thing3: string;
    };
    
    let cols: string[] = ['Thing1', 'Thing2', 'Thing3'];

    let rows: Job[] = [
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
        { thing1: 'foo', thing2: 1, thing3: 'fizz' },
        { thing1: 'bar', thing2: 2, thing3: 'buzz' },
    ];
    // rows.reverse();
</script>

<style>
    table {
        border-style: solid;
        border-width: 1px;
        border-color: rgba(0,0,0,.12);
        margin: 0px;
        padding: 0px;
        border-radius: 4px;
        border-collapse: collapse;
        color: rgba(0, 0, 0, 0.87);
    }

    table th:nth-child(2), td:nth-child(2) { width: 100px; }

    .details {
        colspan: 3;
    }
</style>