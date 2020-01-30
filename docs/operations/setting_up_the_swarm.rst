.. _operations-setting-up-the-swarm:

====================
Setting up the swarm
====================

COPS utilizes :term:`Container Orchestration` provided by docker swarm to manage 
and deploy the various services that comprise the system. In order to deploy COPS 
and to take advantage of everything container orchestration has to offer we must first:

* Install docker-ce on each host.
* Initialize swarm mode on each host.
* Setup the main traefik service.
* Deploy COPS as a stack.

This document will assume that the server operating system is Ubuntu 18.04 
(Bionic Beaver) and that the proper user permissions and SSH access has already been established.

Installing docker
=================

* Update the local database

.. code-block:: bash

   sudo apt-get update

* Download dependencies

.. code-block:: bash

   sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

* Add docker's GPG key

.. code-block:: bash

   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add --

* Install the docker repository

.. code-block:: bash

   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"

* Update repositories

.. code-block:: bash

   sudo apt-get update

* Install docker-ce

.. code-block:: bash

   sudo apt-get install docker-ce

* Add user to docker group

.. code-block:: bash

   sudo usermod -aG docker $USER

* Test to see if docker works

.. note:: If a permissions error occurs the server may need to be restarted.

.. code-block:: bash

   docker run hello-world

Create the swarm
================

.. important:: The following ports will need to be available on the master and worker nodes.

   * TCP port 2376 for secure Docker client communication. This port is required 
     for Docker Machine to work. Docker Machine is used to orchestrate Docker hosts.
   * TCP port 2377. This port is used for communication between the nodes of a 
     Docker Swarm or cluster. It only needs to be opened on manager nodes.
   * TCP and UDP port 7946 for communication among nodes (container network discovery).
   * UDP port 4789 for overlay network traffic (container ingress networking).

* SSH into the server you'd like to initialize as the swarm master.

* Run the following command to initialize docker swarm on the node:

.. code-block:: bash

   docker swarm init

* After this is command is executed properly the output should look like the following:

.. code-block:: shell-session

   Swarm initialized: current node (xxxxxxxxxxxxxxxxxx) is now a manager.

   To add a worker to this swarm, run the following command:

       docker swarm join --token SWMTKN-1-xxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx xxx.xx.xxx.xxx:2377

   To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

* This will have initialized that server as the master node of the swarm. All 
  other hosts that are intended to be part of the swarm need to be added by using 
  the ``docker swarm join`` command from the output. This command will join the other hosts as worker nodes.

* Copy the line with the text and token that looks like this:

.. code-block:: bash

   docker swarm join --token SWMTKN-1-xxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxx xxx.xx.xxx.xxx:2377

* Paste the previous line into a terminal window of all other nodes in the cluster.

Create the main Traefik service
===============================

.. important:: A `DevOps Request <https://github.com/openstax/cnx/wiki/Making-DevOps-Requests>`_ 
will need to be made in order for them to add the openstax.cert and openstax.pem 
files to the server.

* Connect via SSH to a manager node in the swarm.

* Create an environmental variable that has the ``NODE_ID`` as a value.

.. code-block:: bash

   export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')

* Add the following label to the master node in the cluster so that Traefik will 
  always be started on this node.

.. code-block:: bash

   docker node update --label-add proxy=true $NODE_ID

* Create a network that will be shared with Traefik and the containers you will 
  deploy as part of the COPS stack.

.. code-block:: bash

  docker network create --driver=overlay traefik-public

* Create the traefik service using the ``docker service create`` command:

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
