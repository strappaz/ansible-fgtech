# Ansible Inventory Examples

This directory contains example inventory files demonstrating various Ansible inventory features in INI format.

## Files

1. `production.ini` - Production environment inventory with multiple groups and variables
2. `staging.ini` - Staging environment inventory
3. `development.ini` - Development environment inventory with developer workstations

## Key Concepts Demonstrated

### Basic Groups
```ini
[web_servers]
web1.example.com
web2.example.com
```

### Host Variables
```ini
web1.example.com http_port=80 https_port=443
```

### Group Variables
```ini
[web_servers:vars]
http_port=80
https_port=443
```

### Group of Groups (Children)
```ini
[web_cluster:children]
web_servers
load_balancers
```

### Host Ranges
```ini
[development]
web-dev-[01:05].example.com
db-dev-[a:c].example.com
```

### Special Groups
- `all`: All hosts
- `ungrouped`: Hosts not in any group other than 'all'

## Using the Inventory

Specify the inventory file when running Ansible commands:

```bash
ansible all -i inventory/production.ini -m ping
ansible-playbook -i inventory/staging.ini site.yml
```

## Best Practices

1. Use separate inventory files for different environments
2. Group related hosts together
3. Use variables to manage differences between environments
4. Document your inventory structure and variables
5. Use `group_vars/` and `host_vars/` for more complex variable management

## Next Steps

1. Create a `group_vars/` directory for environment-specific variables
2. Add `host_vars/` for host-specific overrides
3. Consider using dynamic inventory scripts for cloud environments
