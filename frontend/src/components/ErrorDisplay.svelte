<Banner
  bind:open
  mobileStacked 
  content$style="max-width: 90%;"
  class="error"
  on:SMUIBanner:closed={handleBannerClosed}
>
  <Label bind:this={label} slot="label" style="overflow-x: scroll; white-space: nowrap;">
    {#if errors.length === 1}
      {errors[0]}
    {:else}
      {#each errors as e, i}
        <div style="display: inline-block; padding: 0px 10px">
          <strong style="padding: 5px; border-radius: 10px; border: 1px solid black;">
            {errors.length - i}.
          </strong> {e}
        </div>
      {/each}
    {/if}
  </Label>
  <Button slot="actions">Okay</Button>
</Banner>
 
<script lang="ts">
  import Banner, { Label } from '@smui/banner'
  import Button from '@smui/button'
  import { onMount } from 'svelte';
  import { errorStore } from '../ts/stores'

  let open = false
  let label
  let errors: string[] = []

  function handleBannerClosed(_event) {
    // The banner will not open again until the error changes
    errorStore.clear()
  }

  onMount(() => {
    errorStore.subscribe(updatedErrors => errors = updatedErrors)
  })

  $: {
    open = false
    if (errors.length > 0) {
      open = true
      label.getElement().scroll({ left: 0, behavior: 'smooth' })
    }
  }
</script>