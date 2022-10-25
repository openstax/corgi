<Dialog
    bind:open
    sheet
>
    {#if selectedJob}
        {#if selectedJob.status.name == "failed"}
            <Header>
                <Title>Job #{selectedJob.id} Errors</Title>
            </Header>
            <Content>
                {selectedJob.error_message}
            </Content>
            <Actions>
                <Button variant="raised" on:click={() => {repeatJob(selectedJob)}}>
                    <Label>Repeat</Label>
                </Button>
                <Button variant="raised" on:click={() => {}}>
                    <Label>Close</Label>
                </Button>
            </Actions>
        {:else}
            <Header>
                <Title>Job #{selectedJob.id} Actions</Title>
            </Header>
            {#if ["completed", "aborted"].includes(selectedJob.status.name)}
                <Actions>
                    <Button variant="raised" on:click={() => {repeatJob(selectedJob)}}>
                        <Label>Repeat</Label>
                    </Button>
                    {#if selectedJob.status.name == "completed"}
                        <Button color="secondary" variant="raised" on:click={() => {}}>
                            <Label>Approve</Label>
                        </Button>
                    {/if}
                    <Button variant="raised" on:click={() => {}}>
                        <Label>Close</Label>
                    </Button>
                </Actions>
            {:else if ["queued", "assigned", "processing"].includes(selectedJob.status.name)}
                <Actions>
                    <Button variant="raised" on:click={() => {abortJob(selectedJob.id)}}>
                        <Label>Abort</Label>
                    </Button>
                    <Button variant="raised" on:click={() => {}}>
                        <Label>Close</Label>
                    </Button>
                </Actions>
            {/if}
        {/if}
    {/if}
</Dialog>

<script lang="ts">
    import Dialog, { Header, Title, Content, Actions, InitialFocus } from '@smui/dialog'
    import Button from '@smui/button'
    import { Label } from '@smui/common'
    import { abortJob, repeatJob } from './ts/jobs'
    import type { Job } from './ts/types'
    import IconButton from '@smui/icon-button';

    export let selectedJob: Job
    export let open
</script>