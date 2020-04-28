const constructImageSource = ({ imageRegistry, imageName, imageTag }) => {
  if (imageRegistry == null || imageName == null) {
    return null
  }
  return {
    repository: `${imageRegistry}/${imageName}`,
    tag: imageTag || 'latest',
    insecure_registries: [imageRegistry]
  }
}

module.exports = {
  constructImageSource
}
