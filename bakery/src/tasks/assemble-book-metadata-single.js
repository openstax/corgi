const { constructImageSource } = require('../task-util/task-util')
const fs = require('fs')
const path = require('path')

const task = (taskArgs) => {
    const imageDefault = {
        name: 'openstax/cops-bakery-scripts',
        tag: 'trunk'
    }
    const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
    const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
    const bookInput = 'book'
    const fetchedInput = 'fetched-book-git'
    const assembledInput = 'assembled-book-git'
    const outputName = 'assembled-book-metadata-git'
    const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/assemble_book_metadata_single.sh'), { encoding: 'utf-8' })

    return {
        task: 'assemble single book metadata',
        config: {
            platform: 'linux',
            image_resource: {
                type: 'docker-image',
                source: imageSource
            },
            inputs: [
                { name: bookInput },
                { name: fetchedInput },
                { name: assembledInput }
            ],
            outputs: [{ name: outputName }],
            params: {
                OUTPUT_NAME: outputName,
                ASSEMBLED_INPUT: assembledInput,
                FETCHED_INPUT: fetchedInput,
                BOOK_INPUT: bookInput
            },
            run: {
                path: '/bin/bash',
                args: [
                    '-cxe',
                    shellScript
                ]
            }
        }
    }
}

module.exports = task
