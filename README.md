# Kuberecon

## Description

Kuberecon is a Python script designed for Kubernetes container reconnaissance.

## Usage

To use the script, execute the following command in your terminal from inside a Kubernetes container:

```bash
python3 kuberecon.py
```

## Current Tests

1) Check if docker.sock exists
2) Check if Kubernetes service account token exists and readable
3) Check for environment variables related to Kubernetes and highlights non-defaults
4) Check for files related to Kubernetes
5) Check for mounts and highlights non-defaults

## Example Output

```bash
root@container:/home# python3 kuberecon.py
 _  __     _            ____
| |/ /   _| |__   ___  |  _ \ ___  ___ ___  _ __
| ' / | | | '_ \ / _ \ | |_) / _ \/ __/ _ \| '_ \
| . \ |_| | |_) |  __/ |  _ <  __/ (_| (_) | | | |
|_|\_\__,_|_.__/ \___| |_| \_\___|\___\___/|_| |_|
by Upwind


[TEST] Check for docker.sock
	[NOT FOUND]

[TEST] Check for service account token
	[EXISTS] Found in path /run/secrets/kubernetes.io/serviceaccount/token

[TEST] List environment variables related to kubernetes
	KUBERNETES_SERVICE_PORT=443
	KUBERNETES_PORT=tcp://172.20.0.1:443
	KUBERNETES_PORT_443_TCP_ADDR=172.20.0.1
	KUBERNETES_PORT_443_TCP_PORT=443
	KUBERNETES_PORT_443_TCP_PROTO=tcp
	KUBERNETES_SERVICE_PORT_HTTPS=443
	KUBERNETES_PORT_443_TCP=tcp://172.20.0.1:443
	KUBERNETES_SERVICE_HOST=172.20.0.1

[TEST] List files related to kubernetes
	/home/kuberecon.py
	/run/secrets/kubernetes.io

[TEST] List mounts to nodes file system
	/dev/nvme0n1p1 on /data type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
	/dev/nvme0n1p1 on /logs type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
	/dev/nvme0n1p1 on /etc/hosts type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
	/dev/nvme0n1p1 on /dev/termination-log type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
	/dev/nvme0n1p1 on /etc/hostname type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
	/dev/nvme0n1p1 on /etc/resolv.conf type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)
```
