<div class="inputContainer">
  <Autocomplete
  options={repos}
  bind:value={repo}
  label="Repo"
  />

  <Autocomplete
  options={repos}
  bind:value={book}
  label="Book"
  />

  <Autocomplete
  options={repos}
  bind:value={version}
  label="Version"
  />
</div>

<div class="inputContainer">
{#each options as option}
  <FormField>
    <Checkbox
      bind:group={selected}
      value={option.name}
      disabled={option.disabled}
    />
    <span slot="label"
      >{option.name}{option.disabled ? ' (disabled)' : ''}</span
    >
  </FormField>
{/each}
</div>

<Button on:click={createNewJob}><Label>Create New Job</Label></Button>

<script lang="ts">
  import LayoutGrid, { Cell } from '@smui/layout-grid';
  import Checkbox from '@smui/checkbox';
  import FormField from '@smui/form-field';
  import Autocomplete from '@smui-extra/autocomplete';
  import Button, { Label } from '@smui/button';
  
  let options = [
    {
      name: 'PDF',
      disabled: false,
    },
    {
      name: 'WebView',
      disabled: false,
    },
    {
      name: 'EPUB',
      disabled: false,
    },
    {
      name: 'Docx',
      disabled: false,
    },
  ];

  export let selected = ['PDF', 'WebView', 'EPUB', 'Docx'];
  
  let repo: string | undefined = undefined;
  let book: string | undefined = undefined;
  let version: string | undefined = undefined;
  
  let filters = [];

  let repos = [
    'osbooks-writing-guide',
    'osbooks-introduction-sociology',
    'osbooks-college-physics-bundle',
    'osbooks-university-physics-bundle',
    'osbooks-american-government',
    'osbooks-precalculo',
    'osbooks-quimica-bundle',
    'osbooks-entrepreneurship',
    'osbooks-us-history',
    'osbooks-principles-finance',
    'osbooks-playground',
    'osbooks-introduction-business',
    'osbooks-calculus-bundle',
    'osbooks-psychologia',
    'osbooks-calculo-bundle',
    'osbooks-biology-bundle',
    'osbooks-psychology',
    'osbooks-fizyka-bundle',
    'osbooks-statistics',
    'osbooks-introduction-anthropology',
    'osbooks-chemistry-bundle',
    'osbooks-physics',
    'osbooks-prealgebra-bundle',
    'osbooks-anatomy-physiology',
    'osbooks-business-ethics',
    'osbooks-business-law',
    'osbooks-microbiology',
  ] 

  function createNewJob() {
      
  }

</script>

<style>
.inputContainer {
  display: inline-block;
}
</style>