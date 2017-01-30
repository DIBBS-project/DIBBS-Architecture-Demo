# DIBBs Architecture Demo

Operations management platform that combines access to data and computation within one geospatial portal. More details can be found in the following paper [docs/publishing_platform_for_geospatial_operations.pdf](https://github.com/DIBBS-project/DIBBS-Architecture-Demo/blob/master/docs/publishing_platform_for_geospatial_operations.pdf).

## Quick-start

1. Get this repo

  ```bash
  git clone https://github.com/DIBBS-project/DIBBS-Architecture-Demo.git
  cd DIBBS-Architecture-Demo
  ```

2. Reset to stable

  ```bash
  git fetch
  git checkout stable
  ```

### Setup

#### with Docker

```bash
sudo bash deploy_with_docker.sh
# answer (y)es to the prompt about resetting repos to stable branch if you
# haven't made any changes (i.e. just cloned the repos).
pip install -r requirements.txt
```

#### without Docker

> *This is currently not maintained and may be broken!*

```bash
sudo bash deploy_without_docker.sh
pip install -r requirements.txt
```

### Run Jobs

#### on ROGER

1. Update your account information in `infrastructure_description_roger.json`

2. Run the following "one liner" script:
  ```
  ./onliner_init_script.sh --run-on-roger
  ```

#### on Chameleon (baremetal)

1. Update your account information in `infrastructure_description_chameleon.json`

2. Edit `RESERVATION_ID` in `create_lc_operation.py` with the *reservation* ID from your lease containing at least 3 nodes.

3. Run the following "one liner" script:

  ```
  ./onliner_init_script.sh
  ```

### Reusing a cluster

1. Make note of the instance ID from the above script. (Hint: it's probably `1` if you've only created one)

2. Call Operation script like below, filling in `<instance_id>` as per above (currently valid users are `alice`, `bob`, `cindy`, `dave`).

    ./create_lc_operation.py run -i<instance_id> --user=bob`

---
(older documentation follows...)

## Installation and run

### Without Docker

> *This method will modify the configuration of the computer, you should run it inside a virtual machine or on a testing computer. If you plan to do testing on your own computer, please consider following the "With Docker" instructions.*

Run the following command:

```shell
sudo bash deploy_without_docker.sh
```

It will install the following software:
- screen
- pip
- redis-server

and the following python packages:
- keystoneauth1
- keystonemiddleware
- python-keystoneclient
- redis
- celery

### With Docker

Run the following command:

```shell
sudo bash deploy_with_docker.sh
```

It will install the following software:
- docker

## Bootstrapping

To bootstrap a newly deployed DIBBs platform (give one or two minutes to the system to run), you will have to do the following actions:

- configure cloud computing infrastructures that will be used to run operation executions
- add some appliances that describes environment in which are run operations

### Configure cloud computing infrastructures and credentials

#### Add a cloud computing infrastructure and credentials

Cloud computing infrastructures and credentials are described in JSON format files. We have included two examples:

| Cloud infrastructure | type | Description file |
| -------------------- | ------------- | ---|
| Chameleon  | OpenStack (bare-metal) | infrastructure\_description\_chameleon.json  |
| Roger  | OpenStack (KVM) |infrastructure\_description\_roger.json |

To add a Cloud Computing infrastructure to an existing DIBBs platform, run the following command (Roger):

```shell
python create_os_users.py infrastructure_description_roger.json
```

#### Description of cloud computing and credentials

```javascript
{
  "credentials": [
    {
      "name": "kvm@roger_dibbs",
      "username": "<username>",
      "project_name": "<project_name>",
      "flavor": "standard",
      "infrastructure": "kvm@roger"
    }
  ],
  "infrastructures": [
    {
      "name": "kvm@roger",
      "contact_url": "http://roger-openstack.ncsa.illinois.edu:5000/v2.0",
      "type": "openstack"
    }
  ]
}
```

### Add appliances

Appliances are a description of a software environment in which operations will be run. Implementation of appliances is based on Heat (OpenStack). In this project, we provide an hadoop appliance which has been used for examples.

To add this hadoop appliance, run the following command:

```shell
python create_appliances.py infrastructure_description_roger.json
```

## Running an example

We provide a small example of a "line counter" operation.


## Architectural annexes

### Concepts

![figures/uml.png](figures/uml.png)
