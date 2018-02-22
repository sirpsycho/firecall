# firecall
Automate SSH communication with firewalls, switches, etc.


# Description

These scripts are designed to automate sending commands to a Cisco ASA firewall.  The intended purpose here is to eliminate the need to manually log in to a firewall to make changes.  This code can be run directly via command line or it can be incorporated into other scripts.  For example, if a honeypot observes malicious activity, it can automatically block the source IP at the firewall level.


# Configuration

The "blockip.py" script is designed to quickly block a host by simply providing the IP address (Usage: `python blockip.py <ip-address>`). 

Before running "blockip.py", open "blockip.conf" in a text editor and enter one or more firewall IP addresses next to "SERVER_LIST" as well as a username, and any other configurations.  Optionally, to further simplify blocking an IP, you can create an alias:

`echo 'alias blockip="python /full/path/to/blockip.py"' >> ~/.bashrc`

This way, you can just type `blockip` and then the ip address that you want to block.

Example usage:
```
# blockip 12.34.56.78
Enter password for user "admin": 
[-] (firewall01) Added IP 'x.x.x.x' to firewall group 'Deny_All_Group'
```


# Dependencies

"paramiko" must be installed for this program to run.  To install paramiko, try running "pip install paramiko".  On Macs, you may have to install a version of Python that has "pip".  To do this, you can use either easy_install or homebrew (run "sudo easy_install pip" or "brew install python")

