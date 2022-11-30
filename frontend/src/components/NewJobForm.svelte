<div class="inputContainer">
  <Autocomplete
    id="repo-input"
    type="email"
    search={searchRepos}
    bind:text={selectedRepo}
    clearOnBlur={false}
    updateInvalid
    label="Repo"
  />

  <Autocomplete
    id="book-input"
    search={searchBooks}
    bind:text={selectedBook}
    on:focus={() => {
      if (selectedRepo !== previousRepo) {
        // The autocomplete component only runs search again when its value
        // changes. To deal with this problem, toggle between null and ''
        // when we want to force updates
        selectedBook = selectedBook == null ? '' : null
        previousRepo = selectedRepo
      }
    }}
    clearOnBlur={false}
    label="Book"
  />

  <Autocomplete
    id="version-input"
    clearOnBlur={false}
    bind:text={selectedVersion}
    label="Version"
  />
</div>

<div class="inputContainer">
  {#each options as option}
    <FormField>
      <Checkbox
        id={`${option.id}-job-option`}
        bind:group={selectedJobTypes}
        value={option.id}
        disabled={option.disabled}
      />
      <span slot="label">
        {option.name}{option.disabled ? " (disabled)" : ""}
      </span>
    </FormField>
  {/each}
</div>
  
<Button
  id="submit-job-button"
  variant="raised"
  color="secondary"
  disabled={!validJob}
  on:click={() => { 
    void clickNewJob(
      selectedRepo,
      selectedBook,
      selectedVersion,
      selectedJobTypes
    )
  }}
>
  <Label>Create New Job</Label>
</Button>
<script lang="ts">
  import { onMount, tick } from "svelte"
  import Checkbox from "@smui/checkbox";
  import FormField from "@smui/form-field";
  import Autocomplete from "@smui-extra/autocomplete";
  import Button from "@smui/button";
  import { Label } from "@smui/common";
  import {
    fetchRepoSummaries,
    filterBooks,
    handleError,
    repoToString,
  } from "../ts/utils";
  import type { RepositorySummary } from "../ts/types";
  import { repoSummariesStore } from "../ts/stores";

  export let selectedRepo = ""
  export let selectedBook = ""
  export let selectedVersion = ""
  export let selectedJobTypes = []
  export let clickNewJob!: (
    selectedRepo: string,
    selectedBook: string,
    selectedVersion: string,
    selectedJobTypes: string[]
  ) => Promise<void>

      let previousRepo: string
  let validJob = false

  let repoSummaries: RepositorySummary[] = []
  let options = [
    { name: "PDF", id: "PDF", disabled: false },
    { name: "WebView", id: "Web", disabled: false },
    { name: "EPUB", id: "EPUB", disabled: true },
    { name: "Docx", id: "Docx", disabled: false },
  ];

  async function getRepoSummaries() {
    if (repoSummaries.length === 0) {
      repoSummaries = await fetchRepoSummaries();
    }
    return repoSummaries;
  }

  function createSearchFunction(
    getOptions: (
      repoSummaries: RepositorySummary[],
      lowerInput: string
    ) => string[]
  ) {
    return async function (input: string) {
      try {
        const repoSummaries = await getRepoSummaries()
        const lowerInput = input?.toLocaleLowerCase().trim()
        const options = getOptions(repoSummaries, lowerInput)
        return options
      } catch (e) {
        handleError(e)
      }
    }
  }

// if we ever want to re-enable filtering repositories on book:
// (!selectedBook && lowerPath.includes(lowerInput)) ||
// repoSummaries.find(rs => 
//   !!repoToString(rs).includes(lowerPath) &&
//   rs.books.find(b => b.includes(selectedBook))
// )
  const searchRepos = createSearchFunction((repoSummaries, lowerInput) => {
    const matches = []
    if (lowerInput == null) {
      lowerInput = ''
    }
    for (const repoPath of repoSummaries.map((repo) => repoToString(repo))) {
      const lowerPath = repoPath.toLocaleLowerCase()
      if (lowerPath.includes(lowerInput)) {
        if (lowerPath === lowerInput) {
          return [repoPath]
        }
        matches.push(repoPath)
      }
    }
    matches.sort()
    return matches
  });

  const searchBooks = createSearchFunction((repoSummaries, lowerInput) => {
    if(lowerInput == null) {
      lowerInput = ''
    }
    const matches = filterBooks(repoSummaries, selectedRepo).filter((bookSlug) =>
      bookSlug.toLocaleLowerCase().includes(lowerInput)
    )
    matches.sort()
    return matches
  });

  async function setSelectedRepo(selectedBook) {
    if (selectedRepo) return
    const repo = repoSummaries.find((r) => r.books.find((b) => b === selectedBook));
    // https://svelte.dev/tutorial/tick
    await tick()
    selectedRepo = repo ? repoToString(repo) : selectedRepo
  }

  onMount(async () => {
    repoSummariesStore.subscribe(updateRepoSummaries => {
      // If something is in the text box, we do not need to force an update
      if (!selectedRepo) {
        // force selectedRepo to update when repoSummaries updates
        selectedRepo = selectedRepo == null ? '' : null
      }
      repoSummaries = updateRepoSummaries
    })
    void repoSummariesStore.update()
  })

  $: validJob = selectedJobTypes.length !== 0 && !!selectedRepo && !!selectedBook
  $: void setSelectedRepo(selectedBook)
</script>