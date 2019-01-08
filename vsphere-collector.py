#!/usr/bin/env python3

import atexit
import json
import os
import pyVim.connect
from pyVmomi import vim, vmodl
import ssl

def create_property_filter(service_content):
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()

    folder_to_child_entity = vmodl.query.PropertyCollector.TraversalSpec(
        name="folderToChildEntity",
        type=vim.Folder,
        path="childEntity",
        skip=False,
        selectSet=[
            vmodl.query.PropertyCollector.SelectionSpec(name="folderToChildEntity"),
            vmodl.query.PropertyCollector.SelectionSpec(name="dcToVmFolder")
        ]
    )

    dc_to_vm_folder = vmodl.query.PropertyCollector.TraversalSpec(
        name="dcToVmFolder",
        type=vim.Datacenter,
        path="vmFolder",
        skip=False,
        selectSet=[
            vmodl.query.PropertyCollector.SelectionSpec(name="folderToChildEntity"),
        ]
    )

    filter_spec.objectSet = [
        vmodl.query.PropertyCollector.ObjectSpec(
            obj=service_content.rootFolder,
            skip=False,
            selectSet=[
                folder_to_child_entity,
                dc_to_vm_folder,
            ]
        )
    ]

    filter_spec.propSet = [
        vmodl.query.PropertyCollector.PropertySpec(
            all=False,
            type=vim.VirtualMachine,
            pathSet=["name", "config.uuid"]
        )
    ]

    property_filter = service_content.propertyCollector.CreateFilter(filter_spec, True)

    atexit.register(property_filter.Destroy)

    return property_filter

def wait_for_updates(service_content, max_updates=100, max_wait=60):
    options = vmodl.query.PropertyCollector.WaitOptions(maxObjectUpdates=max_updates, maxWaitSeconds=max_wait)
    version = ""

    property_collector = service_content.propertyCollector

    while True:
        objects = []

        result = property_collector.WaitForUpdatesEx(version, options=options)
        if result is None:
            continue

        for filter_set in result.filterSet:
            for object_update in filter_set.objectSet:
                obj = object_update.obj

                props = {
                    "obj": str(obj),
                    "kind": object_update.kind,
                    "changeSet": {},
                    "missingSet": {}
                }

                for property_change in object_update.changeSet:
                    props["changeSet"][property_change.name] = str(property_change.val)

                for missing_property in object_update.missingSet:
                    props["missingSet"][missing_property.path] = str(property_change.fault)

                objects.append(props)

        print("%s" % (json.dumps(objects)))

        version = result.version

def main():
    host = os.environ.get("VSPHERE_HOST")
    user = os.environ.get("VSPHERE_USERNAME", "root")
    password = os.environ.get("VSPHERE_PASSWORD")
    port = os.environ.get("VSPHERE_PORT", "443")

    try:
        service_instance = pyVim.connect.SmartConnectNoSSL(host=host, user=user, pwd=password, port=int(port))
    except vim.fault.InvalidLogin as e:
        print("%s: host=%s port=%s user=%s" % (str(e.msg), host, port, user))
        return -1

    atexit.register(pyVim.connect.Disconnect, service_instance)

    service_content = service_instance.RetrieveContent()
    if not service_content:
        print("Could not retrieve service content")
        return -1

    create_property_filter(service_content)
    wait_for_updates(service_content)


if __name__ == "__main__":
	main()
