# 1830PSS Health Check Django Management Commands

This document describes the Django management commands available for administering the 1830PSS Health Check system.

## Available Commands

### hc_setup - Setup and Network Management

The `hc_setup` command manages the integration between the Django application and the external Script directory.

#### Usage Examples

```bash
# Initial setup - verify script integration
python manage.py hc_setup --action setup

# List all configured networks and their status
python manage.py hc_setup --action list

# Validate all networks (check if required files exist)
python manage.py hc_setup --action validate

# Validate a specific network
python manage.py hc_setup --action validate --network "CustomerA"

# Reset all network files (with confirmation)
python manage.py hc_setup --action reset

# Reset specific network files
python manage.py hc_setup --action reset --network "CustomerA"

# Force reset without confirmation
python manage.py hc_setup --action reset --force
```

#### What it does

- **setup**: Verifies Script directory structure, template files, and creates necessary directories
- **list**: Shows all networks with their setup status and file system information  
- **validate**: Checks that network-specific MOP files exist and updates database status
- **reset**: Removes network-specific files and resets database status to NEW

### hc_monitor - System Monitoring and Maintenance  

The `hc_monitor` command provides monitoring and maintenance capabilities.

#### Usage Examples

```bash
# Show overall system status
python manage.py hc_monitor --action status

# Show usage statistics for last 30 days
python manage.py hc_monitor --action stats

# Show statistics for specific network
python manage.py hc_monitor --action stats --network "CustomerA"

# Show statistics for last 7 days
python manage.py hc_monitor --action stats --days 7

# Show failed sessions
python manage.py hc_monitor --action failed

# Clean up files older than 30 days (dry run)
python manage.py hc_monitor --action cleanup --dry-run

# Clean up files older than 60 days
python manage.py hc_monitor --action cleanup --days 60
```

#### What it does

- **status**: Shows system health, network counts, recent activity, disk usage
- **stats**: Displays usage statistics, success rates, network breakdown  
- **failed**: Lists recent failed sessions with error details
- **cleanup**: Removes old session files to free disk space

## Network File Requirements

Per the MOP document, each network requires these files in the Script directory:

- `{NetworkName}_HC_Issues_Tracker.xlsx` - Network-specific tracker template
- `{NetworkName}_ignored_test_cases.txt` - Text-based ignore rules
- `{NetworkName}_ignored_test_cases.xlsx` - Excel-based ignore rules

## Database Status Values

- **NEW**: Network exists but required files are missing
- **READY**: Network has all required files and can process health checks

## Automated Operations

The management commands can be integrated into automated workflows:

### Daily Health Check

```bash
# Check system status and validate networks
python manage.py hc_monitor --action status
python manage.py hc_setup --action validate
```

### Weekly Maintenance

```bash
# Show weekly statistics and clean old files
python manage.py hc_monitor --action stats --days 7
python manage.py hc_monitor --action cleanup --days 30
```

### Monthly Reporting

```bash
# Generate comprehensive monthly report
python manage.py hc_monitor --action stats --days 30
python manage.py hc_monitor --action failed
```

## Integration with MOP Workflow

These commands align with the MOP document procedures:

1. **Initial Setup**: Use `hc_setup --action setup` to verify Script integration
2. **Network Configuration**: Use `hc_setup --action validate` to check MOP file requirements  
3. **Health Monitoring**: Use `hc_monitor --action status` for operational oversight
4. **Issue Investigation**: Use `hc_monitor --action failed` when troubleshooting
5. **Maintenance**: Use `hc_monitor --action cleanup` for disk space management

## Error Handling

Commands provide clear error messages and use Django's standard command framework:

- Use `--traceback` flag for detailed error information
- Use `--verbosity 2` for more detailed output
- Commands will fail safely if prerequisites are missing

## Security Considerations

- Commands respect Django's security model
- File operations are restricted to Script directory
- No sensitive data is exposed in command output
- Reset operations require confirmation unless `--force` is used

## Support and Troubleshooting

If commands fail:

1. Verify Django environment is properly activated
2. Check that Script directory exists and contains required files
3. Ensure database connectivity
4. Review error messages and use `--traceback` for details
5. Contact support team as per MOP documentation
