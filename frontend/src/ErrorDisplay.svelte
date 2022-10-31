<Banner
  bind:open
  centered
  mobileStacked 
  class="error"
  on:SMUIBanner:closed={handleBannerClosed}
>
  <Label slot="label">
    {$error}
  </Label>
  <Button slot="actions">Okay</Button>
</Banner>
 
<script lang="ts">
  import Banner, { Label } from '@smui/banner'
  import Button from '@smui/button'
  import { error } from './ts/stores'

  let open = false

  function handleBannerClosed(_event) {
    // The banner will not open again until the error changes
    error.update(_ => '')
  }

  $: {
    open = false
    if ($error) {
      open = true
    }
  }
</script>