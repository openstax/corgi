.. _operations-updating-the-stack:

================================
Deploying and updating the stack
================================

The entire COPS system is deployed using Docker swarm. Docker swarm provides a ``docker stack`` command that will deploy and update a set of services based on a docker-compose file. Refer to :ref:`operations-setting-up-the-swarm` to do the initial setup of the servers with swarm.

The deployment process is currently done manually (hopefully will be automated in the future) but is fairly straightforward.

The steps at a high level are:

1. Establish an SSH tunnel from ``bastion2.cnx.org`` to the AWS server.
2. Establish an SSH tunnel from your local computer to ``bastion2.cnx.org``.
3. Run the ``./script/build-push.sh`` script to build and push images to dockerhub.
4. Run the ``./script/deploy.sh`` script to deploy or update the stack.

The more granular details of the deployment are explained below.

Install docker-auto-labels
==========================

The docker-auto-labels package is used to ensure the proper labels are applied to the
docker swarm nodes. For example, the database should only be running on ``server1.cops-mvp.openstax.org``.
This is done by applying a label to that node and adding a constraint to the
docker-compose file.

Install the docker-auto-labels package:

.. code-block:: bash

   pip install docker-auto-labels

Setup the SSH tunnel from bastion2 to AWS
=========================================

* Open a fresh terminal window. Keep it open until the end of the deployment process.

* SSH into ``bastion2.cnx.org``

* Run the following command to establish an SSH tunnel to a manager node in AWS:

.. code-block:: bash

   ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -NL localhost:2377:/var/run/docker.sock ubuntu@cc1.cnx.org -i ~/.ssh/cops.pem

This command doesn't produce any output unless there is an error. No other commands
will be typed into this window.

Setup SSH Tunnel from localhost to bastion2
===========================================

* Open a fresh terminal window. Keep it open until the end of the deployment process.

* Run the following command to create an SSH tunnel from localhost to the tunnel created in the previous command:

.. code-block:: bash

   ssh -NL 9999:localhost:2377 bastion2.cnx.org

Setup terminal window for communicating with docker swarm manager node
======================================================================

* Open another fresh terminal window. Keep it open until the end of the process.

* Configure docker in that terminal to use the remote host established before:

.. code-block:: bash

   export DOCKER_HOST="localhost:9999"

.. note:: All docker commands you run in this window will be like running them on the remote host. This window should only be used to run the deploy script.

* Set an environment variable for the ``DOMAIN`` you'd like to deploy to:

.. code-block:: bash

   export DOMAIN="cops.openstax.org"
   export DOMAIN="cops-staging.openstax.org"

* Set an environment variable for the ``STACK_NAME`` you'll be deploying or updating:

.. code-block:: bash

   export STACK_NAME="cops_prod"
   export STACK_NAME="cops_stag"

* Set an environment variable for the ``TRAEFIK_TAG`` for the specific environment. The ``TRAEFIK_TAG`` is used by Traefik to route requests to the proper service. This is useful for separating out production and staging containers.

.. code-block:: bash

   export TRAEFIK_TAG="traefik-public" 
   export TRAEFIK_TAG="traefik-staging"

* Set an environment variable for ``TAG`` which represents the tag for the docker image you'll be pushing to repository.

.. code-block:: bash

    export TAG="latest"
    export TAG="1.1.0"

Build and push new docker images
================================

* Open another fresh terminal window. Keep it open until the end of the deployment process.

* Ensure you have master checked out and the latest codez:

.. code-block:: bash

   git checkout master && git pull origin master

* Tag and upload images to dockerhub. This script builds the images with ``--no-cache`` so may take several minutes.

.. code-block:: bash

   DOMAIN=$DOMAIN TAG=$TAG ./scripts/build-push.sh

Deploy and Update the stack
===========================

* Change to the terminal window where you set the ``DOCKER_HOST`` environmental variable.

* Run the deployment script to update the stack:

.. code-block:: bash

   DOMAIN=$DOMAIN TRAEFIK_TAG=$TRAEFIK_TAG STACK_NAME=$STACK_NAME TAG=$TAG ./scripts/deploy.sh

Cleanup
=======

When the deployment is complete you can close all terminal windows.
