<slot name="data"></slot>
{#if isOpen}
<slot name="details"></slot>
{/if}

<style>
	.box {
		width: 300px;
		border: 1px solid #aaa;
		border-radius: 2px;
		box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
		padding: 1em;
		margin: 0 0 1em 0;
	}
</style>

<script>
      import DataTable, {
            Row
      } from '@smui/data-table';
	import { slide } from "svelte/transition";
	let isOpen = false
	const toggle = () => isOpen = !isOpen
</script>