const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { inputSource, inputPath, validationNames } = taskArgs
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
          from_archive="$(cat book/server)"
          if [[ -n $from_archive ]]
          then
            collection_id="$(cat book/collection_id)"
            xhtmlfiles_path="${inputSource}/$collection_id/"${inputPath}
          else
            xhtmlfiles_path="${inputSource}"${inputPath}
          fi
          for xhtmlfile in $xhtmlfiles_path
          do
            java -cp /xhtml-validator.jar org.openstax.xml.Main "$xhtmlfile" ${validationNames.join(' ')}
          done
        `
        ]
      }
    }
  }
}

module.exports = task
