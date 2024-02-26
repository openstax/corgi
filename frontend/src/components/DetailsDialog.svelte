<script lang="ts">
  import Dialog, { Header, Title, Content, Actions } from "@smui/dialog";
  import CircularProgress from "@smui/circular-progress";
  import Button from "@smui/button";
  import SegmentedButton from "@smui/segmented-button";
  import Segement from "@smui/segmented-button";
  import { Label } from "@smui/common";
  import { abortJob, repeatJob, getErrorMessage } from "../ts/jobs";
  import type { Job } from "../ts/types";
  import { newABLentry, escapeHTML, fetchABL } from "../ts/utils";
  import { ABLStore } from "../ts/stores"
;
  export let selectedJob: Job;
  export let open: boolean;
  let abl;
  let isErrorDialog;
  $: isErrorDialog = selectedJob?.status.name === "failed";
  $: abl = {};

  let disableWorkerCodeVersionCheckbox = false;
  let useWorkerCodeVersion = false;
  
  // [{
  // uuid
  // code_version
  // commit_sha
  // platform
  // }]

  async function getVersions(job: Job) {
    const abl = await fetchABL();
    const anyNew = !job.books.every((book) => abl.find(({ uuid }) => uuid === book.uuid) === undefined);
    if (!anyNew) {
      disableWorkerCodeVersionCheckbox = true;
    }
  }

  function linkToSource(job: Job, msg: string) {
    // Example: ./modules/m59948/index.cnxml:3:1
    // To https://github.com/<owner>/<book>/blob/<version>/modules/m59948/index.cnxml#L3:1
    return msg.replace(
      /\.\/(.+?)(\.cnxml|\.xml):(\d+):(\d+)/g,
      (orig, stem, ext, lineNum, colNum) => {
        const link = document.createElement("a");
        link.dataset.elementType = "error-source-link";
        link.href = encodeURI(
          [
            "https://github.com",
            job.repository.owner,
            job.repository.name,
            "blob",
            job.version,
            `${stem}${ext}#L${lineNum}C${colNum}-L${lineNum}`,
          ].join("/")
        );
        link.rel = "noreferrer";
        link.target = "_blank";
        link.textContent = orig;
        return link.outerHTML;
      }
    );
  }

  ABLStore.subscribe((bookInfos) => {
    const approvedVersionByBookByPlatform = {};
    selectedJob.books.forEach((book) => {
      abl
        .filter((approvedVersion) => approvedVersion.uuid === book.uuid)
        .forEach((approvedVersion) => {
          let obj = approvedVersionByBookByPlatform[approvedVersion.platform];
          if (obj == null) {
            obj = {};
            approvedVersionByBookByPlatform[approvedVersion.platform] = obj;
          }
          obj[book.uuid] = approvedVersion.code_version;
        });
    })
    $abl = approvedVersionByBookByPlatform;
  })

</script>

<Dialog bind:open bind:fullscreen={isErrorDialog} sheet>
  {#if selectedJob}
    <Header>
      <Title>Job #{selectedJob.id}</Title>
      {#if selectedJob.status.name === "completed"}
        <select>
          <!--Platform Selection-->
        </select>
      {/if}
    </Header>
    <Content>
      {#if selectedJob.status.name === "completed"}
        <table>
          <tr>
            <th>Artifact</th>
            <th>Code Version</th>
          </tr>
          {#each selectedJob.artifact_urls as artifact}
          <tr>
            <td>
              <a href={artifact.url} target="_blank" rel="noreferrer">{artifact.slug}</a>
              {#if selectedJob.job_type.name === "git-web-hosting-preview"}
                  <SegmentedButton>
                    <Segement>
                      <label> None </label>
                    </Segement>
                    {#if (abl[platform][artifact.slug].code_version ?? selectedJob.worker_version) !== selectedJob.worker_version }
                    <Segement>
                      <label> abl[platform][artifact.slug].code_version </label>
                    </Segement>
                    {/if}
                    <Segement>
                      <label> selectedJob.worker_version </label>
                    </Segement>
                  </SegmentedButton>
                  {/if}
                </td>
              </tr>
              {/each}
            </table>
      {:else if isErrorDialog}
        {#await getErrorMessage(selectedJob.id)}
          <h3>Fetching error</h3>
          <CircularProgress style="height: 32px; width: 32px;" indeterminate />
        {:then error_message}
          <h3>Error:</h3>
          {#each linkToSource(selectedJob, escapeHTML(error_message ?? "N/A"))
            .trim()
            .split("\n") as line, i}
            <div
              class={`error-line ${line.startsWith("+") ? "trace-text" : ""}`}
            >
              <span class="number">{(i + 1).toString().padStart(5, " ")}</span>
              {@html line}
            </div>
          {/each}
        {:catch requestError}
          <h3>Something went wrong:</h3>
          {requestError.message}
        {/await}
      {/if}
    </Content>
    <Actions>
      {#if ["queued", "assigned", "processing"].includes(selectedJob.status.name)}
        <Button
          id="abort-button"
          variant="raised"
          on:click={() => {
            abortJob(selectedJob.id);
          }}
        >
          <Label>Abort</Label>
        </Button>
      {:else if ["completed", "failed", "aborted"].includes(selectedJob.status.name)}
        <Button
          id="repeat-button"
          variant="raised"
          on:click={() => {
            repeatJob(selectedJob);
          }}
        >
          <Label>Repeat</Label>
        </Button>
        {#if selectedJob.status.name == "completed"}
          <Button
            id="approve-button"
            color="secondary"
            variant="raised"
            on:click={() => {
              newABLentry(selectedJob);
            }}
          >
            <Label>Approve</Label>
          </Button>
        {/if}
      {/if}
      <Button
        variant="raised"
        id="get-link"
        on:click={() => {
          const href = document.location.href.replace(
            document.location.hash,
            ""
          );
          navigator.clipboard.writeText(`${href}#${selectedJob.id}`);
        }}
      >
        <Label>Get Link</Label>
      </Button>
      <Button variant="raised" on:click={() => {}}>
        <Label>Close</Label>
      </Button>
    </Actions>
  {/if}
</Dialog>

<style>
  .error-line {
    white-space: pre-line;
    line-height: 1.5;
    font-size: 12pt;
    font-family: "Courier New", Courier, monospace;
  }

  .error-line > .number {
    white-space: pre;
    font-weight: bold;
    padding: 3px 2px;
    background-color: #ccc;
    user-select: none;
  }

  .trace-text {
    opacity: 0.5;
  }
</style>
