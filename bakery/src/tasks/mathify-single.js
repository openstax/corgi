const dedent = require('dedent')
const { symlink } = require('fs-extra')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/mathify',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const symlinkInput = 'module-symlinks'
  const linkedInput = 'linked-single'
  const styleInput = 'group-style'
  const mathifiedOutput = 'mathified-single'

  return {
    task: 'mathify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: symlinkInput },
        { name: styleInput },
        { name: linkedInput }
      ],
      outputs: [{ name: mathifiedOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${mathifiedOutput}/stderr >&2)
          slug_name="$(cat ${bookInput}/slug)"

          # FIXME: symlinks should only be needed to preview intermediate state
          find "${symlinkInput}" -type l | xargs -I{} cp -P {} "${mathifiedOutput}"

          # Style needed because mathjax will size converted math according to surrounding text
          cp ${styleInput}/* ${linkedInput}

          node /src/typeset/start -i "${linkedInput}/$slug_name.linked.xhtml" -o "${mathifiedOutput}/$slug_name.mathified.xhtml" -f svg  
        `
        ]
      }
    }
  }
}

module.exports = task
