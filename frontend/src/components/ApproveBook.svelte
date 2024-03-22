<script lang="ts">
  import SegmentedButton, { Label, Segment } from "@smui/segmented-button";
  import CircularProgress from "@smui/circular-progress";
  import { ABLStore } from "../ts/stores";
  import type { Job } from "../ts/types";
  import { getLatestCodeVersionForJob, newABLentry } from "../ts/abl";
  import Button from "@smui/button";

  export let selectedJob: Job;
  export let open;
  let selectedCodeVersion;
  let loading = false;

  let choices: Array<string | undefined>;

  $: choices = Array.from(
    new Set(
      [
        getLatestCodeVersionForJob($ABLStore, selectedJob),
        selectedJob.worker_version,
      ].filter((e) => e !== undefined),
    ),
  );
  // Default to first entry
  $: selectedCodeVersion = selectedCodeVersion ?? choices[0];
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
    <div id="approve-action-container">
      <Button
        id="approve-button"
        color="secondary"
        variant="raised"
        disabled={selectedCodeVersion === undefined}
        on:click={() => {
          if (selectedCodeVersion === undefined) {
            throw new Error("No code version selected");
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
