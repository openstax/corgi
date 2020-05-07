.. _operations-clean-up-the-swarm:

==================
Clean Up The Swarm
==================

Add cronjob to run docker prune (MOVE TO CLEANUP)
===============================

Docker swarm does not come with any kind of "garbage collection" for dangling 
volumes or unused containers that are created when doing updates or after 
restarts. This has caused issues where the host nodes run out of hard drive storage. To 
prevent this we have created an :term:`Ansible` playbook to configure a cronjob on the server.

Local or from bastion2?
----------------------

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
