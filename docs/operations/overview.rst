.. _operations-overview:

==============
Overview (WIP)
==============

.. note::
   Currently, the only output that is available is PDF.

The COPS system acts as a central location for users to create jobs and view
their status. When a user creates a job they are needing to produce an output
(PDF, epub, etc) for a book. A book is typically called a collection by Content
Managers and others that work directly with content.

When a job is created it will be placed in a queue. When the output pipeline is
ready it will read the necessary information from the job and begin producing
the output format specified. Upon completion, the job status will be updated with
a completed status and a link for the user to download the specified output.

Currently the COPS swarm lives on our AWS EC2, where the pdf pipeline is.
EC2 cops service really only pertains to the PDF pipeline


EC2 VM where COPS is running AWS EC2 VM bastion2
port 22 EC2 has bastion permission only. 

Network Bastion2 to AWS EC2
with Identity file on your local machine cops.permission


.. blockdiag::

    blockdiag workflow {
       // Set labels to nodes
       A [label = "Cops UI"];
       B [label = "Create Job"];
       C [label = "Job Queued"];
       D [label = "Output Pipeline"];
       E [label = "Output URL"];
      A -> B -> C -> D -> E -> A;
    }


