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

If no hints were included, the RM decides the Site to launch the Cluster on.

If the RM decides to launch a Cluster for an Appliance on a Site and the Site is already hosting a Cluster implementing that same Appliance, the physical cluster is reused. If it does not exist, the Appliance Implementation is loaded for the appropriate Site, and the RM contacts the OpenStack deployment to launch the cluster associated with the Cluster.

After the physical cluster is created/found, the RM also gets or creates credentials for the LL User on that cluster, communicating with an agent on the cluster if needed.

One of the Credentials enumerated in a *hints* key or available to the user making the request is used to select the Site.

Arguments
-----------

* *user* - LL user (obtained via Authentication)
* *name* - A friendly name for display
* *appliance* - The name of the appliance to launch
* *hints* - (Optional) Scheduling information. Accepts an object with optional keys:
  * "credentials" (a list of compute provider credentials available to the user)
  * other appliance-specific information (e.g. number of nodes, lease ID)

Response
-----------

* *id* - Unique ID of cluster for the user's reference
* *credentials* - An object with credentials and connection information as defined by the appliance


CAS: Store Credentials
=========================

Arguments
-------------
* *user* - LL user (obtained via Authentication)
* *name* - Friendly name of the credentials
* *site* - The Site to which these credentials belong
* *credentials* - RSA-OAEP obfuscated credentials


CAS: Get Public Key
=====================

Arguments
-------------
* *user* - LL user (obtained via Authentication)

Response
-------------
* *rsa_public* - RSA public key that can be used to obfuscate credentials for sending back to the server


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

1. Get or create the Cluster. Send a request with authentication to the RM with:

  * the specific Appliance name to use,
  * a friendly name,
  * optionally hints indicating on which Site (compute resources) to run.

If no hints were included, the RM decides the Site to launch the Cluster on. If the user already has a Cluster using the chosen Appliance on the Site the RM decided to use, that Cluster is reused. The Appliance Implementation is loaded for the appropriate Site, and the RM contacts the OpenStack deployment to launch the cluster associated with the Cluster.

The RM waits, polling OpenStack until it has created the hosts, and then creates Host objects to hold some of their details.

The response includes:

  * an ID which is used by subsequent requests to refer to the created object,
  * the IP address of the master node to which connection attempts can be made

2. View the Cluster. A request for the cluster by ID also returns the IP of the master node, to which connections can be made.

3. [Undefined] Modify the Cluster. Issue a request to alter/scale the cluster using the cluster ID.

4. [Unimplemented] Destroy the Cluster. Issue a request using the cluster ID to indicate the resources are no longer needed it.


----------
Objects
----------

Relationship diagram

.. graphviz::

  digraph LL {

  subgraph cluster_rm {
      label = "Resource Manager";
      #style = filled;
      color=red;
      node [shape=record];

      uclust [label="UserCluster"];
      clust [label="Cluster"];
      #clustcred [label="Cluster\nCredentials"];

      uclust -> clust;
  }

  subgraph cluster_cas {
      label = "Auth Service";
      #style = filled;
      color=blue;
      node [shape=record];

      user [label="User"];
      cred [label="Credentials"];

      cred -> user;
  }

  subgraph cluster_ar {
      label = "Appliance Registry";
      #style = filled;
      color=green;
      node [shape=record];

      app [label="Appliance"];
      appim [label="Appliance\nImplementation"];
      site [label="Site"];

      appim -> app;
      appim -> site;
  }

  subgraph cluster_om {
      label = "Operation Manager";
      color=orange;

      node [shape=record];

      exe [label="Execution"];
  }

  clust -> appim;
  cred -> site;
  clust -> cred;
  #clustcred -> user;
  uclust -> user;
  exe -> uclust;

  }


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
Caveats
------------------------------------------

Images
==========

There is currently an out-of-band step required: the Glance VM image used by the Heat template must be uploaded to every site the appliance will be launched on.
