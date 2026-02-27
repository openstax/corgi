<script lang="ts">
  import Dialog, { Header, Title, Content } from "@smui/dialog";
  import Button from "@smui/button";
  import { Label } from "@smui/common";
  import IconButton from "@smui/icon-button";
  import { pipelineVersionStore, versionStore } from "../ts/stores";
  import {
    fetchAvailableTags,
    setPipelineVersions,
  } from "../ts/pipeline-version";
  import { handleError } from "../ts/utils";

  export let open = false;

  const SLOT_LABELS = ["Newest", "Second", "Oldest"];

  let pendingVersions: string[] = ["", "", ""];
  let originalVersions: string[] = ["", "", ""];
  let availableTags: string[] = [];
  let loading = false;
  $: currentVersion = $versionStore.tag;

  $: if (open) void load();

  async function load() {
    loading = true;
    try {
      const results = await Promise.all([
        pipelineVersionStore.update(),
        versionStore.update(),
        fetchAvailableTags(),
      ]);
      availableTags = results[2];
      const current = $pipelineVersionStore;
      originalVersions = [0, 1, 2].map((pos) => {
        const entry = current.find((v) => v.position === pos);
        return entry?.version ?? "";
      });
      pendingVersions = [...originalVersions];
    } catch (e) {
      handleError(e);
    } finally {
      loading = false;
    }
  }

  $: slotTags = SLOT_LABELS.map((_, i) => {
    const current = pendingVersions[i];
    if (current && !availableTags.includes(current)) {
      return [current, ...availableTags];
    }
    return availableTags;
  });

  function promoteLatest() {
    const newest = availableTags[0];
    if (!newest) return;
    pendingVersions = [newest, pendingVersions[0], pendingVersions[1]];
  }

  async function save() {
    const current = $pipelineVersionStore;
    const hasChanges = pendingVersions.some((v, i) => {
      const existing = current.find((c) => c.position === i);
      return (existing?.version ?? "") !== v;
    });
    if (!hasChanges) {
      open = false;
      return;
    }
    if (
      !window.confirm(
        "This will update the active pipeline versions. Are you sure?",
      )
    )
      return;
    loading = true;
    try {
      await setPipelineVersions(
        pendingVersions
          .map((version, position) => ({ position, version }))
          .filter(({ version }) => version !== ""),
      );
      await pipelineVersionStore.updateImmediate();
      open = false;
    } catch (e) {
      handleError(e);
    } finally {
      loading = false;
    }
  }
</script>

<Dialog
  id="pipeline-version-dialog"
  bind:open
  aria-describedby="pipeline-version-content"
  fullscreen
  sheet
>
  <Header>
    <Title id="pipeline-version-title">Pipeline Versions</Title>
    <IconButton action="close" class="material-icons">close</IconButton>
  </Header>
  <Content id="pipeline-version-content">
    <div id="pipeline-version-body">
      <div id="pipeline-version-current-tag">
        Current CORGI Version: <div
          id="pipeline-version-corgi-version"
          class={currentVersion === pendingVersions[0]
            ? "active"
            : "not-active"}
        >
          <!-- {$versionStore.tag ?? "N/A"} -->
          {currentVersion ?? "N/A"}
        </div>
      </div>
      {#each SLOT_LABELS as label, i}
        <div class="slot-row">
          <span class="slot-label">{label}</span>
          <span
            class="slot-original"
            class:changed={pendingVersions[i] !== originalVersions[i]}
          >
            {originalVersions[i] || "—"}
          </span>
          <select
            bind:value={pendingVersions[i]}
            disabled={loading || availableTags.length === 0}
          >
            {#each slotTags[i] as tag}
              <option value={tag}>{tag}</option>
            {/each}
          </select>
        </div>
      {/each}
    </div>
    <div class="actions">
      <Button
        on:click={promoteLatest}
        disabled={loading ||
          availableTags.length === 0 ||
          currentVersion === pendingVersions[0]}
      >
        <Label>Promote Latest</Label>
      </Button>
      <Button on:click={save} disabled={loading}>
        <Label>Save Changes</Label>
      </Button>
    </div>
  </Content>
</Dialog>

<style>
  .slot-row {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1em;
    margin-bottom: 0.5em;
  }

  .slot-label {
    width: 70px;
  }

  .slot-original {
    font-size: 0.85em;
    color: #666;
  }

  .slot-original.changed {
    text-decoration: line-through;
    color: #c00;
  }

  .actions {
    display: flex;
    gap: 0.5em;
    margin-top: 1em;
  }

  #pipeline-version-body {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1em;
  }

  #pipeline-version-current-tag {
    width: 100%;
    text-align: center;
    font-weight: bold;
    font-size: 150%;
  }

  #pipeline-version-corgi-version.not-active {
    color: red;
  }

  #pipeline-version-corgi-version.active {
    color: green;
  }
</style>
