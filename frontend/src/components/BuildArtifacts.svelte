<script lang="ts">
  import type { Job } from "../ts/types";

  export let selectedJob: Job;
</script>

<div id="build-artifacts-frame">
  <h3>Build Artifacts</h3>
  <ul>
    {#each selectedJob.artifact_urls as artifact}
      <li>
        <a href={artifact.url} target="_blank" rel="noreferrer"
          >{artifact.slug}</a
        >
      </li>
    {/each}
  </ul>
</div>

<style>
  #build-artifacts-frame {
    padding: 10px;
    margin: 10px;
    background-color: rgba(255, 128, 0, 0.25);
  }

  #build-artifacts-frame h3:nth-of-type(1) {
    margin-top: 0;
  }
</style>
