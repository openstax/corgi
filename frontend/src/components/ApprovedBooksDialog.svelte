<script lang="ts">
  import DataTable, { Head, Body, Row, Cell, Label } from "@smui/data-table";
  import Dialog, { Header, Title, Content } from "@smui/dialog";
  import { ABLStore } from "../ts/stores";
  import type { ApprovedBookWithDate } from "../ts/types";
  import IconButton from "@smui/icon-button";
  import { getVersionLink, sortBy } from "../ts/utils";
  import VersionLink from "./VersionLink.svelte";

  let sorted: ApprovedBookWithDate[] = [];
  let slice: ApprovedBookWithDate[] = [];

  // Try to update the ABLStore when the dialog opens
  $: if (open === true) void ABLStore.update();
  $: sorted = sortBy($ABLStore, [
    { key: "repository_name" },
    { key: "slug" },
    { key: "consumer" },
    { key: "committed_at", desc: true },
  ]);
  $: slice = sorted;

  function getVersionLinkFromAB(ab: ApprovedBookWithDate) {
    // TODO: Maybe add repository_owner to ApprovedBookWithDate to avoid
    // hardcoding owner
    const repo = { name: ab.repository_name, owner: "openstax" };
    return getVersionLink(repo, ab.commit_sha);
  }

  export let open = false;
</script>

<Dialog bind:open sheet fullscreen aria-describedby="abl-table">
  <Header>
    <Title id="over-fullscreen-title">Approved Books</Title>
    <IconButton action="close" class="material-icons">close</IconButton>
  </Header>
  <Content id="abl-table" style="padding: 0">
    <DataTable
      stickyHeader
      style="width: 100%;"
      table$aria-label="Approved Books"
    >
      <Head>
        <Row>
          <Cell columnId="repo">
            <Label>Repository</Label>
          </Cell>
          <Cell columnId="book">
            <Label>Book</Label>
          </Cell>
          <Cell columnId="commit">
            <Label>Commit</Label>
          </Cell>
          <Cell columnId="commit_date">
            <Label>Commit Date</Label>
          </Cell>
          <Cell columnId="code_version">
            <Label>Min Code Version</Label>
          </Cell>
          <Cell columnId="uuid">
            <Label>UUID</Label>
          </Cell>
          <Cell columnId="consumer">
            <Label>Consumer</Label>
          </Cell>
        </Row>
      </Head>
      <Body>
        {#each slice as item}
          <Row slot="data">
            <Cell>
              {item.repository_name}
            </Cell>
            <Cell>
              {item.slug}
            </Cell>
            <Cell>
              <VersionLink
                href={getVersionLinkFromAB(item)}
                text={item.commit_sha.slice(0, 7)}
              />
            </Cell>
            <Cell>
              {item.committed_at}
            </Cell>
            <Cell>
              {item.code_version}
            </Cell>
            <Cell>
              {item.uuid}
            </Cell>
            <Cell>
              {item.consumer}
            </Cell>
          </Row>
        {/each}
      </Body>
    </DataTable>
  </Content>
</Dialog>
