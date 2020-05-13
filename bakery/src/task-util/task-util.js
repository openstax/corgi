const constructImageSource = ({ registry, name, tag }) => {
  const source = {}
  if (name == null) { return null }
  if (tag != null) { source.tag = tag }
  if (registry != null) {
    source.repository = `${registry}/${name}`
    source.insecure_registries = [registry]
  } else {
    source.repository = name
  }
  return source
}

module.exports = {
  constructImageSource
}
