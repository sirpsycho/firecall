# firecall
Automate SSH communication with firewalls, switches, etc.


# Description

These scripts are designed to automate sending commands to a Cisco ASA firewall.  The intended purpose here is to eliminate the need to manually log in to a firewall to make changes.  This code can be run directly via command line or it can be incorporated into other scripts.  These scripts were created with automation/orchestration in mind - if done securely, these scripts could ingest security intelligence data to automatically block malicious IPs based on certain criteria.


# Configuration

Before running any of these scripts, open up "config" in a text editor and configure each value as applicable.  Make sure to enter one or more firewall IP addresses next to "SERVER_LIST" as well as a username, and any other configurations.

- add multiple firewalls to configure them all simultaneously
- configure email alerting to be alerted when an IP is blocked or un-blocked
- whitelist IPs that you never want to get blocked
- optional logging feature for audit capability

# blockip

The "blockip.py" script is designed to quickly block a host by simply providing the IP address (Usage: `python blockip.py <ip-address>`). 

Optionally, to further simplify blocking an IP, you can create an alias:

`echo 'alias blockip="python /full/path/to/blockip.py"' >> ~/.bashrc`

This way, you can just type `blockip` and then the ip address that you want to block.

Example usage:
```
# blockip 12.34.56.78
[-] (firewall01) Added IP '12.34.56.78' to firewall group 'Deny_All_Group'
```
# removeip

This script works in the same way as blockip, except it removes an IP block from the firewall.  It can be used to quickly "undo" a block made by blockip.

In the same way as above, you can create an alias to make this easier:

`echo 'alias removeip="python /full/path/to/removeip.py"' >> ~/.bashrc`

Example usage:
```
# removeip 12.34.56.78
[-] (firewall01) Successfully removed IP '12.34.56.78' from firewall group 'Deny_All_Group'
```


# Dependencies

"paramiko" must be installed for this program to run.  To install paramiko, try running "pip install paramiko".  On Macs, you may have to install a version of Python that has "pip".  To do this, you can use either easy_install or homebrew (run "sudo easy_install pip" or "brew install python")

