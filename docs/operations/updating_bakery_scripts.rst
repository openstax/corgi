.. _operations-updating-bakery-scripts:

===========================
Update COPS "Bakery" Scripts 
===========================

All scripts that pipeline tasks may use to complete jobs for any COPS Pipelines live in docker image `openstax/cops-bakery-scripts <https://hub.docker.com/repository/docker/openstax/cops-bakery-scripts>`_. 
The scripts are not limited to baking tasks as that name would suggest. 

Updating the bakery scripts and testing it in the pipeline.

SCripts giet merge into docker
you will get a new merge
and new build pipeline gets triggered and images get new targets

ce-image-autotag pipeline

and you can build the pipeliens with those tags

Development
===========

[Bucket Set Up instructions for development here.]
[How can you easily copy the prod bucket with all its permissions?]

when you have made updates to the scripts.. bakery/src/scripts
you can push to dockerhub 
and test your scripts by refereing to the docker images

1. push scripts to image
2. build pipsline foncifg file with pieline command
3. do a find and replace for openstax/cops-bakery-scripts
4. save config file
5. execute the config file.

there's another way to do this with the CLI - reference the readme. 

Production
==========
When you are good with what you see 
let the code be merged
once the code is merged 
autotag occurs and you grab the tag that is used 
[steps here]
to stage it and  then it will get promoted to production. 
