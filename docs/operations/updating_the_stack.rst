.. _operations-updating-the-stack:

=============================
Deploy and Update COPS Stack
=============================
The entire COPS system is deployed using `Docker Swarm <https://docs.docker.com/engine/swarm/>`_. The deployment process is currently done manually (hopefully will be automated in the future) but is fairly straightforward.

Docker Swarm provides a ``docker stack`` command that will deploy and update a set of services based on a docker-compose file. 

Refer to :ref:`operations-setting-up-the-swarm` to do the initial setup of the servers with swarm.


High Level Overview
===================

1. Establish an SSH tunnel from Production server to AWS server. why
2. Establish an SSH tunnel from your local computer to Production server. why
3. Run the ``./script/build-push.sh`` script to build and push images to dockerhub.
4. Run the ``./script/deploy.sh`` script to deploy or update the stack.

Nitty-Gritty Steps
==================

Prerequisites
--------------
Install `Docker Auto Labels <https://github.com/tiangolo/docker-auto-labels>`_. Package used to ensure proper labels are applied to the
docker swarm nodes. 

.. code-block:: bash

   pip install docker-auto-labels

For example, the database should only be running on ``server1.cops-mvp.openstax.org``.
This is done by applying a label to that node and adding a constraint to the
docker-compose file.

Configure Proxy Jump through Bastionn to AWS Server from Local Server. 

.. code-block:: bash
   $ scp brenda@bastion2.cnx.org:~/.ssh/cops.pem ~/.ssh/cops.pem
   $ ls .ssh
      bastion.id_rsa	config	cops.pem	id_rsa		id_rsa.pub	known_hosts

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

.. note:: Assuming that you have a copy of **IdentityFile ~/.ssh/cops.pem** copied and configured where your ssh keys are.


Setup Port Forwarding to AWS by Tunneling Through Bastion2
-------------------------------------------------------
Open a fresh terminal window, keep terminal open until the end of the deployment process.

(set ups yoru enviornment when you go int ot the cops server it  will automatically ttunnel through bastion  two . 
because aws serveer only accdesiisble via bastion. 
Whenever I go to cops I need  to go through bastion2.)
Corresponding tunnel command: ssh cops -NL 9999:/var/run/docker.sock
portfowardsing, cops to docker socket on servier - 

Corresponding tunnel command: 

.. code-block:: bash

   ssh cops -NL 9999:/var/run/docker.sock

**No other commands will be typed into this window.**

Setup Terminal for Communicating with Docker Swarm Manager Node
---------------------------------------------------------------
Open a fresh terminal window, keep terminal open until the end of the deployment process.

**Configure Docker to use remote host established in previous step.**

.. code-block:: bash

   export DOCKER_HOST="localhost:9999"

.. note:: This window should only be used to run the deploy script. All docker commands you run in this window will be like running them on the remote host. 

**No other commands will be typed into this window.**

Set Environment Variables
-------------------------------------

Export Tag Convention - 

.. code-block:: bash

   export TAG=$(date '+%Y%m%d.%H%M%S')

use tag for staging, fi it looks good can promote to production. 
only needs to be done once, don;t overwrite it. 

**For Staging**

.. code-block:: bash

   export DOMAIN="cops-staging.openstax.org"    # domain to deploy or update
   export STACK_NAME="cops_stag"                # stack name to deploy or update
   export TRAEFIK_TAG="traefik-staging"         # tag to route requests to proper service, separates staging and production containers


**For Production**

.. code-block:: bash

   export DOMAIN="cops.openstax.org"      # domain to deploy or update
   export STACK_NAME="cops_prod"          # stack name to deploy or update
   export TRAEFIK_TAG="traefik-public"    # tag to route requests to proper service, separates staging and production containers


Build and Push New Docker Images
-------------------------------------
Open a fresh terminal window, keep terminal open until the end of the deployment process.

**Checkout master with the latest codez**

.. code-block:: bash

   git checkout master && git pull origin master

**Tag and upload images to dockerhub.**

.. code-block:: bash

   DOMAIN=$DOMAIN TAG=$TAG ./scripts/build-push.sh

.. note:: This script builds the images with ``--no-cache`` so may take several minutes.

Deploy and Update the COPS Stack
-------------------------------------

**Switch to the terminal window where you set the ``DOCKER_HOST`` environmental variable.**

**Run deployment script to update the COPS stack**

.. code-block:: bash

   DOMAIN=$DOMAIN TRAEFIK_TAG=$TRAEFIK_TAG STACK_NAME=$STACK_NAME TAG=$TAG ./scripts/deploy.sh

Scaling replicas for production stack (only prod)
by defualt swarm scales to 1 replica - so we can use  the below commands to create 

.. code-block:: bash
   docker service update --replicas 2 cops_prod_backend
   docker service update --replicas 2 cops_prod_frontend

define a replica spins up the exat same image up again.. 
within the back end service give me 2 innstannces (hopefully not on the same node)

What is the purpose 2 nodes purpose for load?
related but are seprate -  - fault tolerance

Cleanup
-------

Close all terminal windows when deployment is complete.
