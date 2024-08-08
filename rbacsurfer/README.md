# Kube Recon

## Description

*rbacSurfer* is a Python script that provides an overview of users in a Kubernetes environment. It displays all users and service accounts, their permissions, namespaces, and associated pods, highlighting high-privilege (HP) entries.


## Usage

*rbacSurfer* uses your local Kubernetes config file to connect to the cluster. Run it from a machine with access to the environment and permissions to list roles, cluster roles, role bindings, cluster role bindings, and pods.

```bash
pip install kubernetes
python3 rbacSurfer.py
```

## Example output

The script will output a csv file in the current folder named `identities.csv`

```bash
root@container:/home# cat identities.csv

Name,Type,Namespace,RBAC,Pods,Is HP,Reason
dcgm-exporter-service-acct,service_account,amazon-cloudwatch,"role:configmaps:get","",True,"configmaps:get"
neuron-monitor-service-acct,service_account,amazon-cloudwatch,"role:configmaps:get","",True,"configmaps:get"
my-service-account,service_account,default,"clusterRole:*:*","ubuntu-deployment-54c48b458b-4qkcz",True,"*:*"
event-generator,service_account,event-generator,"","",False,""
...
...
```
