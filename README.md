# VMware vSphere Collector for Topological Inventory

## Overview
The topological inventory vSphere collector connects to a VMware vSphere vCenter Server and collects all managed objects.

## Running
The collector accepts the following environment variables:
* VSPHERE_HOST - The hostname/ipaddress of a vCenter Server
* VSPHERE_USERNAME - The user to login to the vCenter with, defaults to root
* VSPHERE_PASSWORD - The password for $VSPHERE_USERNAME
* VSPHERE_PORT - The port to connect to, defaults to 443

Example:

```
docker run --rm -t -e VSPHERE_HOST=dev-vc67.example.local -e VSPHERE_USERNAME=root -e VSPHERE_PASSWORD=vmware agrare/topological_inventory-collector-vsphere:0.0.1
```
