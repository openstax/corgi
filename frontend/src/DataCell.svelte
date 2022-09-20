{#if header}
    <th>
        <slot></slot>
    </th>
{:else}
    <td>
        <slot></slot>
    </td>
{/if}

<script lang="ts">
    let header = true;
</script>

<style>
    th {
        font-weight: 500;
    }

    th, td {
        padding: 0px 16px;
        border-bottom-width: 1px;
        border-bottom-style: solid;
        border-bottom-color: rgba(0,0,0,.12);
    }
</style>