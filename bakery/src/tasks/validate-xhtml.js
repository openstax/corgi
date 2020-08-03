const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { inputSource, inputPath, validationName } = taskArgs
  const imageDefault = {
    name: 'openstax/xhtml-validator',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'validate xhtml',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: `${inputSource}` }
      ],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          collection_id="$(cat book/collection_id)"
          for xhtmlfile in "${inputSource}/$collection_id/"${inputPath}
          do
            java -cp /xhtml-validator.jar org.openstax.xml.Main "$xhtmlfile" ${validationName}
          done
        `
        ]
      }
    }
  }
}

module.exports = task
