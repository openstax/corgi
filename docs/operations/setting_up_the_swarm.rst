.. _operations-setting-up-the-swarm:

##################
Managing the Swarm
##################

CORGI is architected to leverage :term:`Container Orchestration` provided by `Docker Swarm <https://docs.docker.com/engine/swarm/>`_ to manage 
and deploy the various microservices that comprise the system. CORGI is deployed using an automated `Continuous Delivery (CD) <https://openstax.atlassian.net/wiki/spaces/CE/pages/494600232/Release+Management#Continuous-Delivery-(Release-when-ready)>`_ pipeline.

***************
CORGI Infrastructure
***************

Docker Swarm is deployed and configured using Amazon Web Services, Terraform, and other technologies. 
The setup and installation is documented in our `CE-Infrastructure <https://openstax.atlassian.net/wiki/spaces/CE/pages/2020737025/CE+Infrastructure>`_ Confluence article.

***************
Releasing CORGI
***************

The `Releasing CORGI <https://openstax.atlassian.net/wiki/spaces/CE/pages/1256521739/Releasing+CORGI>`_ Confluence documentation contains the process for deploying and promoting CORGI into production.

The CORGI `CD pipeline configuration <https://github.com/openstax/ce-pipelines/blob/main/pipelines/auto-deploy-corgi.yml>`_ for deploying to CORGI is in the `ce-pipelines <https://github.com/openstax/ce-pipelines>`_ repository.

*******************************
Deploying CORGI PR environments
*******************************

Developers have the capability of deploying PR environments of the entire CORGI stack. The `instructions <https://github.com/openstax/ce-pipelines#corgi-pr>`_ involve setting up a Concourse pipeline with the ``pr-number`` and ``branch-name``.

*************************
Managing CORGI Basic Auth
*************************

The process for managing the basic authentication for CORGI is in the `Credentials Management documentation <https://openstax.atlassian.net/wiki/spaces/CE/pages/670760961/CORGI+Basic+Auth+Credentials+Management>`_ in Confluence.
