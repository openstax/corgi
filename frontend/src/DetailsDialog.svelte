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
                    <a href={artifact.url}>{artifact.slug}</a>
                {/each}
            {:else if selectedJob.status.name == "failed"}
                {selectedJob.error_message}
            {/if}
        </Content>
        <Actions>
            {#if ["queued", "assigned", "processing"].includes(selectedJob.status.name)}
                <Button variant="raised" on:click={() => {abortJob(selectedJob.id)}}>
                    <Label>Abort</Label>
                </Button>
            {:else if ["completed", "failed", "aborted"].includes(selectedJob.status.name)}
                <Button variant="raised" on:click={() => {repeatJob(selectedJob)}}>
                    <Label>Repeat</Label>
                </Button>
                {#if selectedJob.status.name == "completed"}
                    <Button color="secondary" variant="raised" on:click={() => {newABLentry(selectedJob)}}>
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
    import Button from '@smui/button'
    import { Label } from '@smui/common'
    import { abortJob, repeatJob } from './ts/jobs'
    import type { Job } from './ts/types'
    import { newABLentry } from './ts/utils'

    export let selectedJob: Job
    export let open
</script>