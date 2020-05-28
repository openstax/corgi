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
Filled out the credentials.yml

.. code-block:: bash

    credentials.yml

Make sure the environment variables for the environment you want are good in:

.. code-block:: bash

    bakery/env/<environment>.json 


Build pipeline and give output to the pipeline config file:

.. code-block:: bash

    $ cd bakery
    $ ./build pipeline distribution local -o distribution-pipeline.local.yml


-- docker-compose up, concourse server on port :8100

- Set up local concourse target - Note this version is a more updated version

than what is in production

.. code-block:: bash

    fly -t cops-dev login -c http://localhost:8100 -u dev -p dev


- See concourse server targets

.. code-block:: bash

    fly targets


Will most likely prompt you to sync -

.. code-block:: bash

    fly -t cops-dev sync


Set the pipeline to the concourse server target with pipeline config file- 

.. code-block:: bash
    
    fly -t cops-dev sp -p distribution-pipeline -c distribution-pipeline.local.yml -l credentials.yml


Unpause Pipeline:

.. code-block:: bash
    
    fly -t cops-dev unpause-pipeline -p distribution-pipeline


- Let  it be known as to what the triggers the pipeline:

https://github.com/openstax/output-producer-service/blob/master/bakery/distribution-feed.json
- Let it be known how the s3 bucket needs to be set updated
--- Enable version if not Concourse S3 resource will give a versioning error.
--- Bucket region/ access
--- Distribution-feed.json file that (temporary) triggers pipeline
--- Can be seen on localhost:8100

uses build-bakery
(set the tag)
export tag 

How do you update them?
Where do they update?
run with pipeline?
run with task?

-------

generate script and push to docker.

export a tag for development  nad build and look at it. 
if you need to test with concourse build push 

production 
build-push

Production
==========
Filled out the credentials.yml:

.. code-block:: bash

    credentials.yml

Make sure the environment variables for the environment you want are good in:

.. code-block:: bash

    bakery/env/<environment>.json 

Build Pipeline in bakery/ directory:

.. code-block:: bash
    
    ./build pipeline distribution local -o distribution-pipeline.local.yml

Set Pipeline in concourse with config file:

.. code-block:: bash
    
    fly -t cops-dev sp -p distribution-pipeline -c distribution-pipeline.local.yml -l credentials.yml

Unpause Pipeline:

.. code-block:: bash
    
    fly -t cops-dev unpause-pipeline -p distribution-pipeline