<ErrorDisplay/>
<div style="display: flex; justify-content:center;">
  <div>
    <JobsTable></JobsTable>
  </div>
</div>
 
<script lang="ts">
  import JobsTable from './components/JobsTable.svelte'
  import ErrorDisplay from './components/ErrorDisplay.svelte'
</script>

<style>
:global(html, body) {
  position: relative;
  width: 100%;
  height: 100%;
}

:global(body) {
  color: #333;
  margin: 0;
  padding: 0px;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
}

:global(a) {
  color: rgb(0,100,200);
  text-decoration: none;
}

:global(a:hover) {
  text-decoration: underline;
}

:global(a:visited) {
  color: rgb(0,80,160);
}

:global(label) {
  display: block;
}

:global(input, button, select, textarea) {
  font-family: inherit;
  font-size: inherit;
  -webkit-padding: 0.4em 0;
  padding: 0.4em;
  margin: 0 0 0.5em 0;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 2px;
}

:global(input:disabled) {
  color: #ccc;
}

:global(button) {
  color: #333;
  background-color: #f4f4f4;
  outline: none;
}

:global(button:disabled) {
  color: #999;
}

:global(button:not(:disabled):active) {
  background-color: #ddd;
}

:global(button:focus) {
  border-color: #666;
}

:global(.error) {
  background-color: #f44336 !important;
  color: white;
}
</style>