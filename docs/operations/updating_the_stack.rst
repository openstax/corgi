.. _operations-updating-the-stack:

==================
Updating the Stack
==================

The entire COPS system is deployed using Docker swarm. Docker swarm provides a
``docker stack`` command that will deploy a set of services based on a docker-compose
file. Refer to :ref:`operations-setting-up-the-swarm` to do the initial setup of
the servers with swarm.

The stack can also be updated when there are changes. The deployment process
is currently done manually but is fairly straightforward.

The steps at a high level are:

1. Establish an SSH tunnel from your local computer to one of the swarm management
nodes.
2. Run the ``./script/build-push.sh`` script to build and push images to dockerhub.
3. Run the ``./script/deploy.sh`` script to update the stack.

The more granular details of the deployment are explained below.

Install docker-auto-labels
==========================

The docker-auto-labels package is used to ensure the proper labels are applied to the
docker swarm nodes. For example, the database should only be running on ``cc1.cnx.org``.
This is done by applying a label to that node and adding a constraint to the
docker-compose file.

Install the docker-auto-labels package:

.. code-block:: bash

   pip install docker-auto-labels


Setup the SSH tunnel
====================

Open a fresh terminal window. Keep it open until the end of the deployment process.

Run the following command to establish an SSH tunnel to a manager node:

.. code-block:: bash

   ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -NL localhost:2377:/var/run/docker.sock <user>@cc1.cnx.org

This command doesn't produce any output unless there is an error. No other commands
will be typed into this window.

Setup terminal window for communicating with docker swarm manager node
======================================================================

Open another fresh terminal window. Keep it open until the end of the process.

Configure docker in that terminal to use the remote host established before:

.. code-block:: bash

   export DOCKER_HOST="localhost:2377"

Any docker commands you run in this window will be like running them on
the remote host. This window should only be used to run the deploy script.

Build and push new docker images
================================

Open another fresh terminal window. Keep it open until the end of the deployment process.

Ensure you have master checked out and the latest codez:

.. code-block:: bash

   git checkout master && git pull origin master

Tag and upload images to dockerhub. This script builds the images with ``no-cache``
so may take several minutes.

.. code-block:: bash

   TAG=latest ./scripts/build-push.sh

Update the stack
================

Change to the terminal window where you set the ``DOCKER_HOST`` environmental variable.

Run the deployment script to update the production stack:

.. code-block:: bash

   DOMAIN=cops.cnx.org TRAEFIK_TAG=traefik-public STACK_NAME=cops_prod TAG=latest ./scripts/deploy.sh

Cleanup
=======

When the deployment is complete you can close all terminal windows.
