########################################
Tutorial 2: Complex Appliances on LL
########################################

The template may accept some parameters that could control scaling, for instance, and also returns others, such as the mandatory output that states the IP address of the agent.

What are complex appliances?
=================================

A complex appliance is a way to define multiple resources and orchestrate their deployment for reuse. The core of complex appliances is an orchestration template, which defines multiple resources and plumbs them together to create a richer appliance that could include multiple instances, IP addresses, and security groups.

Heat Basics
================

Heat_ is the orchestration service for OpenStack. AWS has a similar service called CloudFormation_. By writing "templates", deployment and configuration of cloud resources can be automated.

Orchestration
------------------

The orchestration template allows multiple nodes and more to be started, configured, and managed, from one command. Input can also be accepted to control the number and type of nodes, then output can be provided so that a user can directly know where to connect or other application-specific information.

At the most minimal end within LL, templates can start an instance and bind an IP to it so that it is contactable from the public internet.

Instance Configuration
------------------------

One of the difficulties when creating clusters from a template is how to inform the nodes about one another so their installed application(s) can communicate. The manual procedure might look something like: deploy N instances with a generic master/worker image. Log into the first one that will be the master node, set that one as the master, and fill out the connection information for all the workers. Log into all the workers and instruct them to contact the master. You might need to give their host keys to the master, so log back into it and paste them all there. A laborious and tedious process.

Orchestration services can automate this by including small scripts that can be run, and the outputs relayed to other instances for handling in order to fill in such things like host keys, the hosts file, or other configuration files.



Examples
-------------

Chameleon has a few complex appliances that permit users to create clusters in a few clicks.

* NFS
  * Provisions n + 1 nodes, n clients, 1 server.
  * IP address exchange
* Hadoop
  * Provisions n + 1 nodes, n workers, 1 master.
  * Host key exchange


Demo: Deploying Hadoop
========================

Hadoop on Chameleon (pref. Roger for speed of boot). Deploy it with OpenStack

1. Log into Horizon
2. Go to Orchestration tab
3. Copy-paste URL of template
4. Fill in parameters, launch
5. Wait until it's ready
6. Log into head node
7. Run LineCounter

Demo: Modifying a Complex Appliance
==========================================

Limited changes can be made to complex appliances. Example:

1. Launch existing CA
2. Install(?) some other Hadoop program
3. Snapshot image
4. Modify template to point at that new image
5. Create new appliance for that program
6. Define Implementation for Appliance on Site
7. Relaunch CA using new appliance



.. _CloudFormation: https://aws.amazon.com/cloudformation/
.. _Heat: https://wiki.openstack.org/wiki/Heat
