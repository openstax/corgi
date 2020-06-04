.. _distribution-pipeline-steps:

############################
Distribution Pipeline Set Up
############################

Internal Development and/or Debugging of Distribution Pipeline Steps
The approach allows developers / QA to inspect all input / output files for tasks 
to confirm data is being generated as expected.

Each step of the distirbution pipeline can be run individually and step by step.

----

*************
Prerequisites
*************

`Install Docker <https://docs.docker.com/get-docker/>`_
=========================================================

`Install AWS CLI <https://aws.amazon.com/cli/>`_
================================================

Clone output-producer-service
=============================

.. code-block:: bash

    $ git cllone git@github.com:openstax/output-producer-service.git

Install Concourse fly cli
===========================
  
- For Linux, `Download the cli command binary <https://concourse-ci.org/quick-start.html>`_
- For Mac, Install with ``brew cask install fly``.  

----

*****
Steps
*****

Get Concourse Up
================

**1. Start the whole infrastructure, from root of output-proudcer-service**

.. code-block:: bash

   $ cd output-producer-service
   $ docker-compose up -d

**2. Ensure Concourse is up by visiting** `http://localhost:8100 <http://localhost:8100>`_ **in your browser.**

* login:``dev``
* password: ``dev``

You should see no pipelines running.

-------

Set Concourse Pipeline
======================

**1. Target the Concourse Fly Cli to the Concourse server:**

Run ``fly targets``. If you don't see `http://localhost:8100` listed under url, run:

.. code-block:: bash

   fly -t cops-dev login -c http://localhost:8100 -u dev -p dev

We've named this pipeline ``cops-dev``.

.. note:: 
   Production Concourse Target URL: https://concourse-dev0.openstax.org 

**2. Set the pipeline with a name and configurations.**

Must have a configuration file to run the following: :ref:`operations-generate-pipeline-config`.

.. code-block:: bash

    $ cd bakery
    $ fly -t cops-dev sp -p bakery -c distirbution-pipeline.local.yml

We've named this pipeline ``bakery`` and passed in config file ``distirbution-pipeline.local.yml``.

..  warning:: 
    If a mismatch occurs between the **fly cli version** and **Concourse version**
    this can be fixed with the ``fly -t <target_name> sync`` command.

    If it continues to block try running the below and then sync:

    .. code-block:: bash

        fly -t cops-dev login -c http://localhost:8100 -u dev -p dev

**3. Confirm Pipeline Configurations.**

.. code-block:: bash

    apply configuration? [yN]: y
    pipeline created!

**4. Unpause Pipeline**

.. code-block:: bash

   fly -t cops-dev unpause-pipeline -p bakery

The Distribution pipeline has now been set up to take jobs.

-------

Trigger Pipeline Job
====================

[currently we are using distibution-feed.json file]

- Let  it be known as to what the triggers the pipeline: https://github.com/openstax/output-producer-service/blob/master/bakery/distribution-feed.json
- Let it be known how the s3 bucket needs to be set updated
    - Enable version if not Concourse S3 resource will give a versioning error.
    - Bucket region/ access

Watch Pipeline Work
====================

After about 30 seconds the job will start in your
`local Concourse <http://localhost:8100>`_ and you will be able to see the job status on `http://localhost/ <http://localhost/>`_ .
