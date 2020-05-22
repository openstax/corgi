.. _operations-setting-up-the-swarm:

=================
Set Up The Swarm
=================

COPS utilizes :term:`Container Orchestration` provided by `Docker Swarm <https://docs.docker.com/engine/swarm/>`_ to manage 
and deploy the various services that comprise the system. 

In order to deploy COPS and to take advantage of everything container orchestration has to offer we must first:

1. Install Docker-CE on each host
2. Initialize Swarm Mode on each host
3. Setup Main Traefik Service

After set up of the servers with swarm we can then :ref:`operations-updating-the-stack` to the swarm servers.

This document will assume that the server operating system is `Ubuntu 18.04 (Bionic Beaver) <https://releases.ubuntu.com/18.04.4/>`_ and proper user permissions and SSH access has already been established.

.. note:: 

   This process is mostly done manual but we will be porting these steps over to 
   using :term:`Ansible`. Currently, the only steps using Ansible are 
   `Add cronjob to run docker prune`_. 

Prerequisites
=============

Install Docker
--------------

**Update Local Database**

.. code-block:: bash

   sudo apt-get update

**Download Dependencies**

.. code-block:: bash

   sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

**Add Docker's GPG Key**

.. code-block:: bash

   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add --

**Install Docker Repository**

.. code-block:: bash

   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"

**Update Repositories**

.. code-block:: bash

   sudo apt-get update

Install Docker-CE
=================

**Install Docker-CE**

.. code-block:: bash

   sudo apt-get install docker-ce

**Add User to Docker Group**

.. code-block:: bash

   sudo usermod -aG docker $USER

**Test Docker**

.. code-block:: bash

   docker run hello-world

.. note:: If a permission error occurs the server may need to be restarted.

Create Docker Swarm
===================

.. important:: The following ports need to be available on the master and worker nodes.

   | **TCP port 2376** 
   | For secure communication to Docker Client.
   | Required for Docker Machine work and orchestrate Docker hosts.
   |
   | **TCP port 2377** 
   | For communication between nodes of a Docker Swarm or cluster.
   | Only needs to be opened on manager nodes.
   |
   | **TCP and UDP port 7946** 
   | For communication among nodes (container network discovery).
   |
   | **UDP port 4789** 
   | For overlay network traffic (container ingress networking).

**STEP 1: SSH into the server you'd like to initialize as the swarm master.**

**STEP 2: Initialize Docker Swarm on Node**

Initialize master node on server:

.. code-block:: bash

   docker swarm init

Successful run will produce the following:

.. code-block:: shell-session

   Swarm initialized: current node (xxxxxxxxxxxxxxxxxx) is now a manager.

   To add a worker to this swarm, run the following command:

       docker swarm join --token SWMTKN-1-xxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx xxx.xx.xxx.xxx:2377

   To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

.. note:: ``docker swarm init`` initiates the server as the Master Node of the swarm and provides a ``docker swarm join ..`` command to join all other hosts intended to be part of the swarm as worker nodes.
   

**STEP 3: Join Worker Nodes to Swarm**

Copy ``docker swarm join`` command with token from ``docker swarm init`` output

.. code-block:: shell-session

   docker swarm join --token SWMTKN-1-xxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx xxx.xx.xxx.xxx:2377

Paste ``docker swarm join..`` command into a terminal window of all other nodes in the swarm.

Create Main Traefik Service
===========================

.. important:: A `DevOps Request <https://github.com/openstax/cnx/wiki/Making-DevOps-Requests>`_ 
   needs to be made in order for devops to add the openstax.cert and openstax.pem 
   files to the server.

**STEP 1: Connect via SSH to a master node in swarm**

**STEP 2: Create node environment variable**

.. code-block:: bash

   export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')

**STEP 3: Add node label to the master node in the swarm**

.. code-block:: bash

   docker node update --label-add proxy=true $NODE_ID

.. note:: Traefik will always be started on this node.

**STEP 4: Create shared network for Traefik and containers deployed as part of stack**

.. code-block:: bash

  docker network create --driver=overlay traefik-public

**STEP 5: Create Traefik Service:**

.. code-block:: bash

   docker service create \
     --name traefik \
     --constraint=node.labels.proxy==true \
     --publish 80:80 \
     --publish 443:443 \
     --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
     --mount type=bind,source=/etc/ssl,target=/etc/ssl \
     --network traefik-public \
     --label "traefik.enable=true" \
     --label "traefik.tags=traefik-public" \
     --label "traefik.docker.network=traefik-public" \
     --label "traefik.redirectorservice.frontend.entryPoints=http" \
     --label "traefik.redirectorservice.frontend.redirect.entryPoint=https" \
     --label "traefik.webservice.frontend.entryPoints=https" \
     traefik:v1.7 \
     --docker \
     --docker.swarmmode \
     --docker.watch \
     --docker.exposedbydefault=false \
     --constraints=tag==traefik-public \
     --entrypoints='Name:http Address::80 Redirect.EntryPoint:https' \
     --entrypoints='Name:https Address::443 TLS:/etc/ssl/certs/openstax.crt,/etc/ssl/private/openstax.pem' \
     --logLevel=INFO \
     --accessLog

Clean Up The Swarm
==================

Add cronjob to run docker prune
-------------------------------

Docker swarm does not come with any kind of "garbage collection" for dangling 
volumes or unused containers that are created when doing updates or after 
restarts. This has caused issues where the host nodes run out of hard drive storage. To 
prevent this we have created an :term:`Ansible` playbook to configure a cronjob on the server.

Local or from bastion2?
-----------------------

There are two places you can run this playbook.

1. From ``localhost`` if you have ``bastion2`` setup as a :term:`JumpHost` and proper key 
   to cops servers in the correct directory.
2. From ``bastion2`` directly.

See this `guide <https://github.com/openstax/cnx/wiki/Configure-bastion2.cnx.org-as-a-JumpHost>`_ 
in the `ConEng wiki <https://github.com/openstax/cnx/wiki>`_ to learn how to configure a :term:`JumpHost`.

If you are running from ``bastion2`` you will need to clone down the 
`output-producer-service repository <https://github.com/openstax/output-producer-service>`_ 
into your home directory and execute the commands.

Running the playbook
--------------------

* Ensure you are in the root directory of  the project and change directory into 
  the ``./ansible`` directory.

.. code-block:: bash

   cd ./ansible

* Create a virtualenv for installing `Ansible <https://docs.ansible.com/ansible/latest/index.html>`_ and dependencies

.. code-block:: bash

   python -m .venv venv

* Activate the virtualenv

.. code-block:: bash

   source ./.venv/bin/activate

* Install requirements.txt

.. code-block:: bash

   pip install -r requirements.txt

.. important:: The following steps depend on where you are running the ``ansible-playbook`` command. 

* Run the :term:`Ansible` playbook for ``bastion2`` as :term:`JumpHost`

.. code-block:: bash

   ansible-playbook -i inventory.jumphost.yml main.yml

* Run the Ansible playbook if you are logged into ``bastion2.cnx.org``

.. code-block:: bash

   ansible-playbook -i inventory.yml main.yml

* You should see the following as output:

.. code-block:: bash

   PLAY [OpenStax COPS deployment] ************************************************

   TASK [Gathering Facts] *********************************************************
   ok: [default]

   TASK [Create cronjob to do docker cleanup] *************************************
   changed: [default]

   PLAY RECAP *********************************************************************
   default  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0