<script lang="ts">
  export let href: string
  export let text: string
</script>

<a
  data-control-type="link-version"
  href={href}
  target="_blank"
  rel="noreferrer"
>
  {text}
</a>