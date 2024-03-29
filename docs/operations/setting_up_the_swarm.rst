.. _operations-setting-up-the-swarm:

##################
Managing the Swarm
##################

CORGI is architected to leverage :term:`Container Orchestration` provided by `Docker Swarm <https://docs.docker.com/engine/swarm/>`_ to manage 
and deploy the various microservices that comprise the system. CORGI is deployed using an automated `Continuous Delivery (CD) <https://openstax.atlassian.net/wiki/spaces/CE/pages/494600232/Release+Management#Continuous-Delivery-(Release-when-ready)>`_ pipeline.

*********************
CORGI Infrastructure
*********************

Docker Swarm is deployed and configured using Amazon Web Services, Terraform, and other technologies. 
The setup and installation is documented in our `CE-Infrastructure <https://openstax.atlassian.net/wiki/spaces/CE/pages/2020737025/CE+Infrastructure>`_ Confluence article.

***************
Releasing CORGI
***************

The `Releasing CORGI <https://openstax.atlassian.net/wiki/spaces/CE/pages/1256521739/Releasing+CORGI>`_ Confluence documentation contains the process for deploying and promoting CORGI into production.

The CORGI `CD pipeline configuration <https://github.com/openstax/ce-pipelines/blob/main/pipelines/auto-deploy-corgi.yml>`_ for deploying to CORGI is in the `ce-pipelines <https://github.com/openstax/ce-pipelines>`_ repository.

***********************************
Troubleshooting CORGI in Production
***********************************

The CORGI system is managed by our container orchestration, Docker Swarm. We utilize automation to talk directly with Docker Swarm for operations. The deployment to staging sets the tag for the images that should be used and the production step simply takes the same tag and rolls it over automatically. This is very similar to a Blue/Green deployment. Our `release pipeline <https://github.com/openstax/corgi/blob/main/scripts/deploy.sh#L24>`_ utilizes a method similar to how a user would manually manage a swarm. Follow the `instructions in Confluence <https://openstax.atlassian.net/wiki/spaces/CE/pages/2020737025/CE+Infrastructure#ssh-connect>`_ if you need to manage the swarm directly.

