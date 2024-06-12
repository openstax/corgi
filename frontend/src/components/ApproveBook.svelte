<script lang="ts">
  import SegmentedButton, { Label, Segment } from "@smui/segmented-button";
  import CircularProgress from "@smui/circular-progress";
  import { ABLStore } from "../ts/stores";
  import type { Job } from "../ts/types";
  import { getExistingCodeVersion, newABLentry } from "../ts/abl";
  import Button from "@smui/button";
  import { Icon } from "@smui/common";
  import { repoToString } from "../ts/utils";

  export let selectedJob: Job;
  export let open: boolean;

  let selectedCodeVersion: string | undefined;
  let loading = false;
  let choices: string[] = [];
  let isValidEntry: boolean = false;

  const updateChoices = async () => {
    const existingVersion = await getExistingCodeVersion(
      $ABLStore,
      selectedJob,
    );
    if (existingVersion === undefined) {
      choices = [];
    } else {
      const { worker_version: workerVersion } = selectedJob;
      choices =
        workerVersion === existingVersion
          ? [workerVersion]
          : [existingVersion, workerVersion];
    }
    // Default to first entry (or undefined)
    selectedCodeVersion = choices[0];
  };

  $: if (open === true) {
    loading = true;
    updateChoices().finally(() => {
      loading = false;
    });
  }
  $: isValidEntry = selectedCodeVersion !== undefined;
</script>

<div id="approve-book-frame">
  {#if loading}
    <h3>Adding ABL entry</h3>
    <CircularProgress style="height: 32px; width: 32px;" indeterminate />
  {:else}
    <h3>Add to ABL</h3>
    <label id="selected-code-version-label" for="selected-code-version"
      >Selected Minimum Code Version:</label
    >
    {#if choices.length > 0}
      <SegmentedButton
        id="selected-code-version"
        segments={choices}
        let:segment
        singleSelect
        bind:selected={selectedCodeVersion}
      >
        <Segment {segment}>
          <Label>{segment}</Label>
        </Segment>
      </SegmentedButton>
    {:else}
      <div style="color: red; display: flex; align-items: center;">
        <Icon class="material-icons">error</Icon>
        <div>Could not get options for code version</div>
      </div>
    {/if}
    <div id="approve-action-container">
      <Button
        id="approve-button"
        color="secondary"
        variant="raised"
        disabled={!isValidEntry}
        on:click={() => {
          const message = [
            "Are you sure you wish to add the following to the ABL?",
            "",
            "Code Version:",
            `    ${selectedCodeVersion}`,
            "Repository:",
            `    ${repoToString(selectedJob.repository)}`,
            "Commit sha:",
            `    ${selectedJob.version}`,
            "Books:",
            `    ${selectedJob.books.map((b) => b.slug).join(", ")}`,
          ];
          if (!confirm(message.join("\n"))) {
            return;
          }
          loading = true;
          newABLentry(selectedJob, selectedCodeVersion)
            .then(() => {
              void ABLStore.update();
              open = false;
            })
            .finally(() => {
              loading = false;
            });
        }}
      >
        <Label>Approve</Label>
      </Button>
    </div>
  {/if}
</div>

<style>
  #approve-book-frame {
    padding: 10px;
    margin: 10px;
    background-color: rgba(0, 255, 128, 0.25);
  }

  #approve-book-frame h3:nth-of-type(1) {
    margin-top: 0;
  }

  #selected-code-version-label {
    font-weight: bold;
  }

  #approve-action-container {
    display: flex;
    justify-content: end;
    margin-top: 10px;
  }
</style>
