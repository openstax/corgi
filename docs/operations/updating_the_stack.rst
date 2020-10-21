.. _operations-updating-the-stack:

############################
Update and Deploy COPS Stack
############################

**********************
The 2-Part Stack Story 
**********************
The COPS Stack is composed of 2 parts, the **COPS System** (Backend, Frontend, etc.) and **COPS Pipeline**.
The parts can be deployed separately, but we've decided to keep the entire COPS stack 
in sync, by making sure they are always deployed together.  

Therefore, if changes are only made to the COPS Pipeline the COPS System (Docker Swarm) will still need a deployed . 
Vice versa, if changes are made to the COPS System a new COPS Pipeline will need to be set. 

1. The COPS System is deployed using `Docker Swarm <https://docs.docker.com/engine/swarm/>`_. 
=============================================================================================

Docker Swarm provides a ``docker stack`` command that will deploy and update a set of services based on a docker-compose file.  

Refer to :ref:`operations-setting-up-the-swarm` to do the initial setup of the servers with swarm.

2. The COPS Pipeline is set on a Concourse server.
==================================================

The COPS pipeline is set up using Concourse through the use ``fly`` commands, Concourse's CLI.

*****************
Overview of Steps
*****************

Set Up SSH Tunnel
   - Set up Portforwarding to AWS by Tunneling through Bastion2. Bastion2 is the only with permission to talk to the AWS Server. Where our COPS Stack is deployed.
   - Set up Terminal for Communication with Docker Swarm Manager Node
Deploy COPS Stack to Staging
   - Deployment to Staging with newly build and tagged images to make sure new images work.
Promote COPS Stack to Production
   - Promote the COPS Stack to Production after successful deploy to Staging.
Build and Push Docker Images
   - Build, Tag, and Push updated images.

----

*************
Prerequisites
*************
1. Install `Docker Auto Labels <https://github.com/tiangolo/docker-auto-labels>`_
=================================================================================
This will ensure proper labels are applied to the docker swarm nodes.

**It is recommended to install docker-auto-labels, deploy to staging, and promote to production in a python virtual enviornment.**

.. code-block:: bash

   pip install docker-auto-labels

For example, the database should only be running on ``server1.cops-mvp.openstax.org``.
This is done by applying a label to that node and adding a constraint to the
docker-compose file.

2. Set up Port Forward to COPS Server (AWS) through Bastion2
============================================================

**Make sure you already have local identity files to:**

   - ``bastion2.cnx.org`` (e.g. at ~/.ssh/bastion2_id_rsa)
   - ``cops.openstax.org`` (e.g. at ~/.ssh/cops.pem).


**Configure your** ``~/.ssh/config`` **with identity files:**

.. code-block:: bash

   Host bastion2
      HostName bastion2.cnx.org
      User <user>
      IdentityFile ~/.ssh/id_rsa
      ForwardAgent yes
   Host cops
      User ubuntu
      HostName cops.openstax.org
      IdentityFile ~/.ssh/cops.pem
      ProxyJump bastion2
      ForwardAgent yes

You can copy down your ``cops.pem`` into your ``~/.ssh`` from bastion2 by:

.. code-block:: bash

   $ cd ~/.ssh/
   $ scp <user>@bastion2:~/.ssh/cops.pem .

.. note:: Example above assumes that a copy of ``cops.pem`` for  **IdentityFile** is copied to where your ssh keys are.


----

***********************
COPS Stack Deploy Steps
***********************

0. Update Buildout and JS Dependencies
===========================================

**Make sure you are checked out to the** `git-ref` **of the latest output-producer-service tagged deploy.**  

.. code-block:: bash

   $ cd output-producer-service
   $ git checkout <git-ref>
   $ git pull

Refer to :ref:`operations-find-git-ref` to find a git-ref with given TAG.

**Update/install JS libraries regularly for the fly command later:**

.. code-block:: bash

   $ cd bakery 
   $ npm install    # yarn v1.x also works
   $ cd ..

1. Set Up SSH Tunnel to COPS
============================  

**In a fresh terminal window, establish an SSH tunnel to a manager node in AWS:**

.. code-block:: bash

   ssh cops -NL 9999:/var/run/docker.sock

This will port forward COPS Server to Local Docker Socket. This command doesn't produce any output unless there is an error.

**Keep terminal open until the end of the deployment process. No other commands will be typed into this window.**

2. Deploy COPS System to Staging Swarm
======================================

.. note:: This window should only be used to run the deploy script.
   All docker commands you run in this window will be like running them on the remote host.

**In a fresh terminal window, configure Docker to use the remote host (established prior):**

.. code-block:: bash

   $ export DOCKER_HOST="localhost:9999"

The above command will set up the terminal window to communicate with Docker Swarm Manager Node 
that was set up in the previous step.  

**Continue in terminal window, set staging environment variables:**

.. code-block:: bash

   $ source ./scripts/vars.staging.sh

The above script will set the staging environment variables for your deploy.

**Continue in terminal window, set code version tag environment variable:**

.. code-block:: bash

   export TAG="tag-of-your-choosing"  ## i.e. 20200612.204804

The above command will set the environment variable for the code version of your choice.    

Refer to :ref:`operations-select-code-version-tag` to find a tag.  

**Continue in terminal window, deploy to staging:**

.. code-block:: bash

   ./scripts/deploy.sh

The above script will deploy the Docker Swarm System with the previously set staging environment variables.

.. warning::
   The deploy script will fail and exit without deploying if any of the required environment variables are not set.

3. Set up COPS Pipeline, on Concourse
=====================================

**Continue in the same terminal from deploy, login to Concourse via** ``fly`` **:**

.. code-block:: bash

   fly login -t concourse-v6 -c https://concourse-v6.openstax.org/ -n CE

**Continue in terminal window, deploy the corresponding pipeline to** ``concourse-v6`` **(BASH shell):**

.. code-block:: bash

   fly -t concourse-v6 sp -p cops-staging -c <(./bakery/build pipeline cops staging --tag $TAG)

The above ``fly`` command will set a new pipeline named ``cops-staging`` with staging pipeline variables.
The above assumes ``fly`` is installed. Depending on your environment, you may need to get the correct 
version of fly from the UI.

4. Promote Staging to Production
================================
Once Staging COPS stack looks good (Steps 3 & 4) ensure SSH tunnel to COPS is still up (Step 2).

**Continue in terminal window, promote staging to deploy:**

.. code-block:: bash

   ./scripts/promote-deploy.sh

The above deployment script will automatically detect the tag deployed to staging and deploy it to production.
There is no need to set any environment variables for production or pick a tag.

**Continue in terminal window, deploy the corresponding pipeline to** ``concourse-v6`` **:**

.. code-block:: bash

   fly -t concourse-v6 sp -p cops-prod -c <(./bakery/build pipeline cops prod --tag $TAG)

----

The above ``fly`` command will set a new pipeline named ``cops-prod`` with production pipeline variables.

5. Cleanup
==========
Close all terminal windows when deployment is complete.

----

***************************
Rotating Basic Auth Secrets
***************************

To update basic auth secrets for COPS, a dev must copy an ``htaccess`` file sourced from AWS SecretsManager and rotate the secret in the swarm with:

.. code-block:: bash
   # ... Properly target the COPS swarm through ssh and set DOCKER_HOST
   # And then:
   export COPS_HTACCESS_FILE=</path/to/file>
   ./scripts/rotate-auth-secrets.sh

This script will rotate the secrets temporarily on COPS staging (so that the caller can ensure that the rotation works as expected) and then the caller can accept the change, in which case the secret is propagated to both staging and prod in a more permanent fashion (and the old secret will be removed).
Rotation in the manner above will likely lead to inability to login for a very brief period of time (less than 30sec).
