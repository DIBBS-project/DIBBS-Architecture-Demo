===================================
Resource Management
===================================

LambdaLink resource management is designed to provide 'common' computational resources to higher-level operations, providing a backend-agnostic interface to where those resources physically are (Chameleon, ROGER, XSEDE, etc.). The resource management is split into two services: one to store definitions and other "cold" information, and the other to manage active resources.

The concept is partially modeled on other cloud services' execution environments and runtimes, where the developer's software in those cases includes metadata declaring the environment they expect (e.g. Python, JavaScript). The service creates the resources then passes control to the software.

----------------------------------
Methods
----------------------------------

RM: Get/Create Cluster
==========================

Get or create a Cluster object based on the desired Appliance.

If no hints were included, the RM decides the Site to launch the Cluster on. If the user already has a Cluster using the chosen Appliance on the Site the RM decided to use (see *hints*), that Cluster is reused. The Appliance Implementation is loaded for the appropriate Site, and the RM contacts the OpenStack deployment to launch the cluster associated with the Cluster.

One of the Credentials enumerated in a *hints* key or available to the user making the request is used to select the Site.

Arguments
-----------

* *user* - LL user (obtained via Authentication)
* *name* - A friendly name for display
* *appliance* - The name of the appliance to launch
* *targeted_slave_count* - Desired number of slaves in the appliance
* *hints* - (Optional) Scheduling information. Accepts an object with optional keys:
  * "credentials" (a list of named credentials)
  * "lease_id" (arbitrary code)

Response
-----------

* *id* - Unique ID of cluster
* *master_node_ip* - IP address of the head node


RM: Get/Create Account
=============================

Get or create credentials for a LL User on the specified Cluster. If the User:Cluster pair is not found in the database, it issues a command to the RM agent running on the cluster to create a new user and associates it with the LL user.

Arguments
-----------

* *user* - LL user (obtained via Authentication)
* *cluster* - ID of the cluster

Response
------------

* *credentials* - Object with credential information defined as per Appliance.


CAS: Store Credentials
=========================

Arguments
-------------
* *user* - LL user (obtained via Authentication)
* *name* - Friendly name of the credentials
* *site* - The Site to which these credentials belong
* *credentials* - RSA-OAEP encrypted (obfuscated) credentials


CAS: Get Public Key
=====================

Arguments
-------------
* *user* - LL user (obtained via Authentication)

Response
-------------
* *rsa_public* - RSA public key that can be used to encrypt (obfuscate) credentials for sending back to the server


AR: Create Appliance
=========================

Arguments
-------------
* *user* - LL user (obtained via Authentication)
* *name* - Unique name of the appliance. Referred to by operations.
* *description*
* *logo_url*


AR: Create ApplianceImplementation
=========================================

Arguments
-------------
* *user* - LL user (obtained via Authentication)
* *appliance* - Name of the appliance that is to be implemented
* *site* - Site this implementation works on
* *image_name* - Name of the OpenStack image (unused since Heat templates)
* *logo_url*


AR: Create Site
==================

Arguments
-------------
* *name* - Name of the site, referred to by Appliance Implementations.
* *type* - "openstack", maybe later "xsede"?
* *contact_url* - Root API URL for the site (Keystone for OS)


----------------------------------
Workflow
----------------------------------

First the appliance data must be loaded into the registry so the manager can use it to instantiate resources. Most of these would be performed one-by-one by a user, rather than in an automated fashion.

1. Create Site entries
2. Create Credential entries for a LL user so the service can act upon an OpenStack deployment on behalf of the user
3. Create Appliance with unique name
4. Create Appliance Implementation for the Appliance by uploading a Heat template that implements the Appliance on a Site.

Running, e.g. by the Operation Manager.

1. Create the Cluster. Send a request to the RM (``POST /clusters``) with:

  * the specific Appliance name to use,
  * a friendly name,
  * the number of slaves in the Cluster, and
  * optionally hints indicating on which Site (compute resources) to run.

If no hints were included, the RM decides the Site to launch the Cluster on. If the user already has a Cluster using the chosen Appliance on the Site the RM decided to use, that Cluster is reused. The Appliance Implementation is loaded for the appropriate Site, and the RM contacts the OpenStack deployment to launch the cluster associated with the Cluster.

The RM waits, polling OpenStack until it has created the hosts, and then creates Host objects to hold some of their details.

The response includes:

  * an ID which is used by subsequent requests to refer to the created object,
  * the IP address of the master node to which connection attempts can be made

2. View the Cluster. A request for the cluster by ID also returns the IP of the master node, to which connections can be made.

3. [Unsure if working] Modify the Cluster. Issue a request to add/delete a host using the cluster ID that will cause the Cluster to increase/decrease by **one** host.

4. [Unimplemented] Destroy the Cluster. Issue a request using the cluster ID to delete it


----------
Objects
----------

Resources that are available to the LambdaLink architecture are defined and stored in the Appliance Registry. These are "at rest" objects.

Appliances
===============

Appliances are named and are referred to by operations as the resources they require to run.


Appliance Implementations
==============================

An implementation of an appliance that provides the concrete definition (scripts) on how to make a compatible appliance on a target site.


Sites
===============

A list of compute services available to LambdaLink. Contains information needed in order to utilize the compute services (URL, API type), except for credentials.


Credentials
==================

Credentials for compute services relating users to sites. Needed to allow LambdaLink to perform OpenStack operations on behalf of a user.


Cluster
=========

The active form of an appliance implementation. Created or reused for a higher-level operation.  Stores outputs from the creation of the Heat stack, which can be queried by the operation's software for required parameters. Responsible for freeing the compute resources when no longer required.


Cluster Credentials
======================

Relates users on a cluster to users within LambdaLink. Stores the cluster users' credentials. [Is this outside the scope of the architecture? This was added to support multiple users for a single runtime instance.]

------------------------------------------
Missing Objects
------------------------------------------

Images?
==========

There is currently an out-of-band step required: the Glance VM image used by the Heat template must be uploaded to every site the appliance will be launched on.


------------------------------------------
Other Objects in current implementation
------------------------------------------

Scripts?
===============

[Currently these are tied to implementations (many scripts:one impl), so I'm not sure how they would be selected if there was more than one. Could we just store the script as an implementation? The implementation could have a date/version/rev field. -NT]


Actions???
===============

[I have no clue what these are for or how they are used. It's implemented as a list of words that scripts relate to. Vestigial from homebrew Heat-esque Mr. Cluster? -NT]


Host
=========

[Vestigial, appears unneeded if Heat is used to manage stack creation -NT]
