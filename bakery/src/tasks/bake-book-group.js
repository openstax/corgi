const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cnx-easybake',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const assembledInput = 'assembled-book-group'
  const recipeInput = 'cnx-recipes-output'
  const symlinkInput = 'module-symlinks'
  const bakedOutput = 'baked-book-group'
  const styleOutput = 'group-style'

  return {
    task: 'bake book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: symlinkInput },
        { name: assembledInput },
        { name: recipeInput }
      ],
      outputs: [
        { name: bakedOutput },
        { name: styleOutput }
      ],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${bakedOutput}/stderr >&2)

          # FIXME: We assume that every book in the group uses the same style
          # This assumption will not hold true forever, and book style + recipe name should
          # be pulled from fetched-book-group (while still allowing injection w/ CLI)

          # FIXME: Style devs will probably not like having to bake multiple books repeatedly,
          # especially since they shouldn't care about link-extras correctness during their
          # work cycle.

          # FIXME: Separate style injection step from baking step. This is way too much work to change a line injected into the head tag
          style_file="cnx-recipes-output/rootfs/styles/$(cat ${bookInput}/style)-pdf.css"

          recipe_file="cnx-recipes-output/rootfs/recipes/$(cat ${bookInput}/style).css"

          # FIXME: symlinks should only be needed to preview intermediate state
          find "${symlinkInput}" -type l | xargs -I{} cp -P {} "${bakedOutput}"

          if [[ -f "$style_file" ]]
          then
            cp "$style_file" ${bakedOutput}
            cp "$style_file" ${styleOutput}
          else
            echo "Warning: Style Not Found" > ${bakedOutput}/stderr
          fi

          for collection in $(find "${assembledInput}/" -path *.assembled.xhtml -type f); do
            slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
            cnx-easybake -q "$recipe_file" "${assembledInput}/$slug_name.assembled.xhtml" "${bakedOutput}/$slug_name.baked.xhtml"
            if [[ -f "$style_file" ]]
            then
              sed -i "s%<\\/head>%<link rel=\"stylesheet\" type=\"text/css\" href=\"$(basename $style_file)\" />&%" "${bakedOutput}/$slug_name.baked.xhtml"
            fi
          done
        `
        ]
      }
    }
  }
}

module.exports = task
