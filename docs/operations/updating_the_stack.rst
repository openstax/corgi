.. _operations-updating-the-stack:

############################
Update and Deploy COPS Stack
############################
The entire COPS system is deployed using `Docker Swarm <https://docs.docker.com/engine/swarm/>`_. The deployment process is currently done manually (hopefully will be automated in the future) but is fairly straightforward.

Docker Swarm provides a ``docker stack`` command that will deploy and update a set of services based on a docker-compose file. 

Refer to :ref:`operations-setting-up-the-swarm` to do the initial setup of the servers with swarm.

After updates have been made to the Stack, the following need to happen - 

----

********
Overview
********

Tunnel Docker Stack to COPS Server (AWS)
   - Set up Portforwarding to AWS by Tunneling through Bastion2. Bastion2 is the only with permission to talk to the AWS Server. Where our COPS Stack is deployed. 
   - Set up Terminal for Communication with Docker Swarm Manager Node
Build and Push Docker Images to Staging
   - Build, Tag, and Push updated images.
Deploy COPS Stack to Staging
   - Deployment to Staging with newly build and tagged images to make sure new images work.
Promote COPS Stack to Production
   - Deployment to Production after successful deploy to Staging.

----

*************
Prerequisites
*************
1. Install `Docker Auto Labels <https://github.com/tiangolo/docker-auto-labels>`_
=================================================================================
This will ensure proper labels are applied to the docker swarm nodes. 

.. code-block:: bash

   pip install docker-auto-labels

For example, the database should only be running on ``server1.cops-mvp.openstax.org``.
This is done by applying a label to that node and adding a constraint to the
docker-compose file.

.. note:: Example above assumes that a copy of ``cops.pem`` for  **IdentityFile** is copied to where your ssh keys are.


2. Set up Port Forward to COPS Server (AWS) through Bastion2
============================================================
**Securely copy your ``cops.pem`` identity file from Bastion:**

.. code-block:: bash

   local:~$ scp <user>@bastion2.cnx.org:~/.ssh/cops.pem ~/.ssh/cops.pem
   local:~$ ls .ssh
      bastion.id_rsa	config	cops.pem	id_rsa		id_rsa.pub	known_hosts

**Configure your** ``~/.ssh/config`` **with** ``cops.pem`` **:**

.. code-block:: bash

   Host bastion2
      HostName bastion2.cnx.org
      User <user>
      IdentityFile ~/.ssh/id_rsa
      ForwardAgent yes
   Host cops
      User ubuntu
      HostName server1.cops-mvp.openstax.org
      IdentityFile ~/.ssh/cops.pem
      ProxyJump bastion2
      ForwardAgent yes

----

*****
Steps
*****

Tunnel Docker to COPS Server
============================

1. Port Forward COPS Server to Local Docker Socket
--------------------------------------------------
**Open a fresh terminal window, and run tunneling command:**

.. code-block:: bash

   ssh cops -NL 9999:/var/run/docker.sock

**Keep terminal open until the end of the deployment process. No other commands will be typed into this window.**

2. Setup Terminal for Communicating with Docker Swarm Manager Node
------------------------------------------------------------------
**Open a fresh terminal window, and set (staging) environment variables:**

.. code-block:: bash

   $ export DOCKER_HOST="localhost:9999"
   $ export TAG=$(date '+%Y%m%d.%H%M%S')          # how do we generate this tag?
   $ export DOMAIN="cops-staging.openstax.org"    # domain to deploy or update
   $ export STACK_NAME="cops_stag"                # stack name to deploy or update
   $ export TRAEFIK_TAG="traefik-staging"         # tag to route requests to proper service, separates staging and production containers

**Keep terminal open until the end of the deployment process.**

.. note:: This window should only be used to run the deploy script. 
   All docker commands you run in this window will be like running them on the remote host.

Build & Push Docker Images to Staging
=====================================
1. Checkout output-producer-service master with the latest codez
------------------------------------------------------------------
**Open a fresh terminal window, pull latest codez:**

.. code-block:: bash

   git checkout master && git pull origin master

2. Build Images with Tag and Push to Dockerhub
----------------------------------------------
**Same terminal window as above, run handy script:**

.. code-block:: bash

   DOMAIN=$DOMAIN TAG=$TAG ./scripts/build-push.sh

.. note:: This script builds the images with ``--no-cache`` so may take several minutes.

**Keep terminal open until the end of the deployment process.**

Deploy to Staging
=================
1. Run deployment script to update the COPS stack
-------------------------------------------------
**Switch to the terminal window where you set the** ``DOCKER_HOST`` **environmental variable.**

.. code-block:: bash

   DOMAIN=$DOMAIN TRAEFIK_TAG=$TRAEFIK_TAG STACK_NAME=$STACK_NAME TAG=$TAG ./scripts/deploy.sh

2. Ensure deployment went well with tagged images by running 
------------------------------------------------------------
(Clarify: Confirm this is the right way to do this.)

.. code-block:: bash

   docker service ls

----

Promote to Production
=====================

1. Update Staging Variables to Production Variables
---------------------------------------------------
**Switch to the terminal window where you set the** ``DOCKER_HOST``, and set (production) environment variables:**

.. code-block:: bash

   $ unset DOCKER_HOST
   $ export DOMAIN="cops.openstax.org"      # domain to deploy or update
   $ export STACK_NAME="cops_prod"          # stack name to deploy or update
   $ export TRAEFIK_TAG="traefik-public"    # tag to route requests to proper service, separates staging and production containers

.. note:: Tag only needs to be declared once and not overwritten. 
   If the deployment to staging looks good the tag can be promoted to production. 

2. Run deployment script to update the COPS stack
-------------------------------------------------
**Switch to the terminal window where you set the** ``DOCKER_HOST`` **environmental variable.**

.. code-block:: bash

   DOMAIN=$DOMAIN TRAEFIK_TAG=$TRAEFIK_TAG STACK_NAME=$STACK_NAME TAG=$TAG ./scripts/deploy.sh

3. Ensure deployment went well with tagged images by running 
------------------------------------------------------------
(Clarify: Confirm this is the right way to do this. Highly don't think so)

.. code-block:: bash

   docker service ls

4. Scale the Replicas for Updated COPS Stack (Already done by Thomas)
---------------------------------------------------------------------
On production you will also need to scale the replicas again after deployment.
By defualt docker swarm scales to 1 replica, (Clarify: we want 2 and hope it's not on the same node - fault tolerance).

.. code-block:: bash

   $ docker service update --replicas 2 cops_prod_backend
   $ docker service update --replicas 2 cops_prod_frontend

----

Cleanup
=======
Close all terminal windows when deployment is complete.
