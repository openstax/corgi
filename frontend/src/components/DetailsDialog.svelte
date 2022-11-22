<Dialog
  bind:open
  sheet
>
  {#if selectedJob}
    <Header>
      <Title>Job #{selectedJob.id}</Title>
    </Header>
    <Content>
      {#if selectedJob.status.name == "completed"}
        {#each selectedJob.artifact_urls as artifact}
          <a href={artifact.url} target="_blank">{artifact.slug}</a>
          <br>
        {/each}
      {:else if selectedJob.status.name === "failed"}
        {#await getErrorMessage(selectedJob.id)}
          <h3>Fetching error</h3>
          <CircularProgress style="height: 32px; width: 32px;" indeterminate />
        {:then error_message}
          <h3>Error:</h3>
          <pre>{error_message}</pre>
        {:catch requestError}
          <h3>Something went wrong:</h3>
          {requestError.message}
        {/await}
      {/if}
    </Content>
    <Actions>
      {#if ["queued", "assigned", "processing"].includes(selectedJob.status.name)}
        <Button id="abort-button" variant="raised" on:click={() => {abortJob(selectedJob.id)}}>
          <Label>Abort</Label>
        </Button>
      {:else if ["completed", "failed", "aborted"].includes(selectedJob.status.name)}
        <Button id="repeat-button" variant="raised" on:click={() => {repeatJob(selectedJob)}}>
          <Label>Repeat</Label>
        </Button>
        {#if selectedJob.status.name == "completed"}
          <Button id="approve-button" color="secondary" variant="raised" on:click={() => {newABLentry(selectedJob)}}>
            <Label>Approve</Label>
          </Button>
        {/if}
      {/if}
      <Button variant="raised" on:click={() => {}}>
        <Label>Close</Label>
      </Button>
    </Actions>
  {/if}
</Dialog>

<script lang="ts">
  import Dialog, { Header, Title, Content, Actions, InitialFocus } from '@smui/dialog'
  import CircularProgress from '@smui/circular-progress';
  import Button from '@smui/button'
  import { Label } from '@smui/common'
  import { abortJob, repeatJob, getErrorMessage } from '../ts/jobs'
  import type { Job } from '../ts/types'
  import { newABLentry } from '../ts/utils'

  export let selectedJob: Job
  export let open
</script>