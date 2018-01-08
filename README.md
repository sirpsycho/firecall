# firecall
Automate SSH communication with firewalls, switches, etc.


# Description

These scripts are designed to automate sending commands to a Cisco ASA firewall.  The "blockip.py" script is designed to quickly block an IP address by simply providing the IP address (Usage: python blockip.py <ip-address>)

NOTE:  Before running "blockip.py", open it in a text editor and enter a valid server address and username.


# Dependencies

"paramiko" must be installed for this program to run.  To install paramiko, try running "pip install paramiko".  On Macs, you may have to install a version of Python that has "pip".  To do this, you can use either easy_install or homebrew (run "sudo easy_install pip" or "brew install python")

