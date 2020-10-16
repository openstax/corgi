const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
  const inputName = 'fetched-book-group'
  const assembledOutput = 'assembled-book-group'
  const symlinkOutput = 'module-symlinks'
  const rawCollectionDir = `${inputName}/raw`

  return {
    task: 'assemble book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: inputName }
      ],
      outputs: [
        { name: assembledOutput },
        { name: symlinkOutput }
      ],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${assembledOutput}/stderr >&2)
          for collection in $(find "${rawCollectionDir}/collections/" -type f); do
            slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
            rm -rf temp-assembly

            mv "$collection" "${rawCollectionDir}/modules/collection.xml"
            
            # Assembly destination must nested EXACTLY one level under cwd for symlinks to work 
            neb assemble "${rawCollectionDir}/modules" temp-assembly/

            # We shouldn't we need this symlink
            rm temp-assembly/collection.xml

            find temp-assembly -type l | xargs -I{} cp -P {} "${symlinkOutput}"
            find "${symlinkOutput}" -type l | xargs -I{} cp -P {} "${assembledOutput}"
            cp "temp-assembly/collection.assembled.xhtml" "${assembledOutput}/$slug_name.assembled.xhtml"
          done
          `
        ]
      }
    }
  }
}

module.exports = task
