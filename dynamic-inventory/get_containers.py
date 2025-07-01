#!/usr/bin/env python

import docker
import json
import argparse

def get_ssh_port(container):
    """
    Finds the host port mapped to the container's port 22/tcp.
    Returns the host port as a string, or None if not found.
    """
    try:
        # Port bindings are nested and can be complex. We need to find the one for 22/tcp.
        bindings = container.attrs['HostConfig']['PortBindings']
        if '22/tcp' in bindings and bindings['22/tcp'] is not None:
            return bindings['22/tcp'][0]['HostPort']
    except (KeyError, IndexError):
        # This happens if there are no port bindings or no mapping for port 22.
        pass
    return None

def generate_inventory():
    """
    Generates the Ansible inventory by inspecting local Docker containers.
    """
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "children": [
                "ungrouped",
                "docker_containers"
            ]
        },
        "docker_containers": {
            "hosts": []
        }
    }

    try:
        # Connect to the local Docker daemon using the default socket
        client = docker.from_env()
        containers = client.containers.list()
    except Exception as e:
        # If Docker is not running or accessible, return an empty inventory
        # print(f"Could not connect to Docker daemon: {e}")
        return inventory

    for container in containers:
        ssh_port = get_ssh_port(container)

        # We only add containers that expose a port 22 to the inventory
        if ssh_port:
            container_name = container.name
            
            # Add the container to the main group
            inventory["docker_containers"]["hosts"].append(container_name)

            # Define the connection variables for this container
            inventory["_meta"]["hostvars"][container_name] = {
                # Ansible will connect to the Docker host's IP
                "ansible_host": "127.0.0.1",
                # on the dynamically mapped port
                "ansible_port": ssh_port,
                # Assume a user and key (in a real scenario, get this from labels)
                "ansible_user": "root",
                "ansible_ssh_private_key_file": "~/.ssh/id_rsa_docker_test",
                "docker_image": container.image.tags[0] if container.image.tags else 'unknown'
            }
            
            # Dynamically create groups based on the container image name
            try:
                image_name_group = container.image.tags[0].split(':')[0].replace('/', '_')
                if image_name_group not in inventory:
                    inventory[image_name_group] = {"hosts": []}
                inventory[image_name_group]["hosts"].append(container_name)
            except IndexError:
                pass # Happens for images without tags

    return inventory

def main():
    """
    Main function to parse arguments and print the inventory.
    """
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory for local Docker containers with SSH.")
    parser.add_argument('--list', action='store_true', help='List all inventory groups and hosts.')
    parser.add_argument('--host', help='Get all variables about a specific host.')
    args = parser.parse_args()

    if args.list:
        inventory_data = generate_inventory()
        print(json.dumps(inventory_data, indent=2))
    elif args.host:
        # A full implementation would rediscover just this host's vars.
        # For this example, returning an empty JSON is sufficient.
        print(json.dumps({}))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
