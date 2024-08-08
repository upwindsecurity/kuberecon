# PEreef

## Description

*PEreef* is a bash script that reveals the permissions of service accounts in a Kubernetes environment. Utilizing `curl` and `awk`, it iterates through all resources and permissions to verify what is allowed with the current token.
*Why Bash?* It's compatible with most environments without requiring additional packages (as long as `curl` is installed).
*Why Use This Script?* PEreef helps you identify potential privilege escalation (PE) opportunities within a container by listing all your permissions and highlighting notable ones.

## Usage

To use the script, execute the following command in your terminal from inside a Kubernetes container:

```bash
./pereef.sh
```

## Example output

The script will output a csv file in the current folder named `permissions.csv`
```bash
root@container:/home# cat permissions.csv

API Group,Resource,Verb,Known High Privilege
,bindings,create,
,componentstatuses,get,
,componentstatuses,list,
,configmaps,create,Yes
,configmaps,delete,Yes
,configmaps,deletecollection,
,configmaps,get,Yes
,configmaps,list,Yes
,configmaps,patch,Yes
,configmaps,update,Yes
,configmaps,watch,
,endpoints,create,
,endpoints,delete,
,endpoints,deletecollection,
,endpoints,get,
,endpoints,list,
,endpoints,patch,
...
...
```
