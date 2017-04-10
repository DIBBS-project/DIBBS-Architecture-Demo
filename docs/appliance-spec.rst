===================================
Appliance Specification
===================================

Requirements that appliances in the LambdaLink system must implement to interact with the system. Beyond the template and the agent, the rest is beyond the concern of the resource management layer. The combination of the IP returned by the template and the credentials by the agent are provided "up" to the operation-executor layer to use as needed.


Template
===========

The Appliance begins with an OpenStack (OS) Heat orchestration template (template). The template is executed on OS sites in order to provision the resources. On the template level, there are parameters that must be accepted and output. The template must also start agents that adhere to an API that allows control by LL.

Templates are unique for each OS site, which constitutes an 'Implementation'. Glance images that the templates refer to must be loaded out-of-band.


Input Parameters
------------------

* `allowed_ip` - An IP that must be allowed to have port 80 access to the agent.
* `cluster_size` - Number of instances to launch in the cluster.


Outputs Parameters
--------------------

* `master_ip` - Public address of the agent.


Agent API
==============

The agent, an HTTP service running on port 80 of the `master_ip` returned by the template, provides a method for LL to manage the appliance.


POST /new_account/
----------------------

Returns a new set of credentials that will be stored in LL and associated with a LL user. What the credentials refer to varies with what the appliance is.

* Parameters: None
* Response: JSON with the following keys
  * `username` - string
  * `password` - string
