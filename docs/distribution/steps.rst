.. _distribution-pipeline-steps:

============================
Pipeline Steps - Development
============================

Internal Development and/or Debugging of Distribution Pipeline Steps
====================================================================

The approach allows developers / QA to inspect all input / output files for tasks 
to confirm data is being generated as expected.

You need docker and the concourse ``fly`` cli command installed. You can download 
the cli command binary for linux or install it on mac with ``brew cask install fly``.

Each step of the distribution pipeline can be run individually and step by step.

Get Concourse up and running before you go through the steps
------------------------------------------------------------

Clone the repo and start the whole infrastructure with

.. code-block:: bash

   docker-compose up -d

You can check if concourse is running by going with your browser to

* `http://localhost:8100 <http://localhost:8100>`_
* login:``dev``
* password: ``dev``

You should see no pipelines running

Sync and connect fly with Concourse
```````````````````````````````````

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


Run tasks using ``fly``
```````````````````````

TODO

