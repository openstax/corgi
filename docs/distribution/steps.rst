.. _distribution-pipeline-steps:

###############
Pipeline Set Up
###############

***********
Development
***********


Overview
========

Internal Development and/or Debugging of Distribution Pipeline Steps
The approach allows developers / QA to inspect all input / output files for tasks 
to confirm data is being generated as expected.

Each step of the distribution pipeline can be run individually and step by step.


Prerequisites
=============

docker
concourse ``fly`` download the cli command binary for linux or install it on mac with ``brew cask install fly``.  
aws cli

1. Get Concourse up and running before you go through the steps
---------------------------------------------------------------

Clone the repo and start the whole infrastructure with

.. code-block:: bash
   $ cd output-producer-service
   $ docker-compose up -d

You can check if concourse is running by going with your browser to

* `http://localhost:8100 <http://localhost:8100>`_
* login:``dev``
* password: ``dev``

You should see no pipelines running

2. Sync and Connect fly with Concourse
--------------------------------------

Sometimes there is a version mismatch and we need to sync fly with our Concourse 
version in use. To do that it is recommend to first run this command:

.. code-block:: bash

   fly sync -c http://localhost:8100

Now we connect ``fly`` cli with our concourse server and name this connection ``cops-dev``

.. code-block:: bash

   fly -t cops-dev login -c http://localhost:8100 -u dev -p dev




Setup the pipeline for accepting jobs
`````````````````````````````````````

.. code-block:: bash

   fly -t cops-dev sp -p bakery -c bakery/pdf-pipeline.local.yml

and confirm with ``y``.

Now unpause the pipeline

.. code-block:: bash

   fly -t cops-dev unpause-pipeline -p bakery

Select a collection for the job and start the PDF pipeline
``````````````````````````````````````````````````````````

Go to `http://localhost/ <http://localhost/>`_ and start a job with your collection of your choice in the UI.

For example:
* Collection: col12081
* Version: latest
* Style: hs-physics
* Content-Server: staging

after a few seconds (it takes maybe 20-30 seconds) you can see the job starting in 
`local Concourse <http://localhost:8100>`_ and in the `local COPS UI <http://localhost>`_.

Beecause the pdf-pipeline is not in our interested here it is recommended to 
stop/cancel the job in the `Concourse <http://localhost:8100>`_ and press the red X 
for cancelling the job.

Start the distribution pipeline steps manually step by step
-----------------------------------------------------------

Generate task definition files
``````````````````````````````

.. code-block:: bash

   cd bakery

if you have not already install necessary packages with

.. code-block:: bash

   yarn

and build the yml task definition files:

.. code-block:: bash

   ./build task look-up-book > look-up-book.yml
   ./build task fetch-book > fetch-book.yml
   ./build task assemble-book > assemble-book.yml
   ./build task assemble-book-metadata > assemble-book-metadata.yml
   ./build task bake-book > bake-book.yml
   ./build task bake-book-metadata > bake-book-metadata.yml
   ./build task checksum-book > checksum-book.yml
   ./build task disassemble-book > disassemble-book.yml
   ./build task jsonify-book > jsonify-book.yml



Make sure the environment variables for the environment you want are good in:
the part you have to fill out:
 distirbution bucket 
  "S3_DIST_BUCKET": "ce-contents-cops-distribution-373045849756",
  "VERSIONED_FILE": "distribution_feed.json"

pdf bucket only needs 
"S3_PDF_BUCKET": "my-bucket",

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

concourse-dev0

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

Run tasks using ``fly``
```````````````````````

TODO

**********
Production
**********