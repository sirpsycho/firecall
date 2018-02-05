#!/usr/bin/python


########################################
##                                    ##
##  CONFIGURE THE FOLLOWING OPTIONS:  ##
##                                    ##
########################################


# Enter SSH server IP or hostname ("192.168.0.1", "switch01", etc.)
server = ""


# Enter SSH username ("admin", "cisco", etc.)
username = "admin"


# (OPTIONAL) Enter SSH password (leave blank to be prompted when you run the script)
password = ""


# (OPTIONAL) Enter SSH private key path (if public key authentication is set up) ex. "/home/user/.ssh/id_rsa"
sshkey = ""


# Name of the group within the firewall that the IP will be added to (to block an IP, this group should already be 
#  defined in the FW and set up in an ACL to be blocked)
firewallGroupName = "Deny_All_Group"


# Enter SSH port (default 22)
port = 22


# Log file location (leave blank to disable logging)
logfile = ""








import firecall
import sys
import os
import datetime
import socket
import getpass


def printhelp():
    print("Usage: python blockip.py <ip-address>\n\nEnter an IP to block on a firewall.  Before running, edit this script and enter a server address and username.\n")

def format_date(date):
    return date.strftime('%m-%d-%Y %H:%M:%S UTC')

def write_log(line):
    if logging:
        with open(logfile, 'a') as f:
            f.write("%s %s\n" % (format_date(datetime.datetime.now()), line))

def alreadyBlocked(ip):
    cmdstring = "sh run object-group id %s" % firewallGroupName
    output = firecall.main(username, password, sshkey, server, port, cmdstring)
    if "AUTOADD_%s_" % ip in output:
        return True
    else:
        return False

def isip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def removeip():
    cmdstring = """configure terminal
object-group network Deny_All_Group
no network-object object %s
no object network $s""" % (objname, objname)
    firecall.main(username, password, sshkey, server, port, cmdstring)

def addip():
    desc = "Added by '%s' via script on %s" % (username, today)
    cmdstring = """configure terminal
object network %s
host %s
description %s
object-group network %s
network-object object %s
write mem""" % (objname, blockip, desc, firewallGroupName, objname)
    firecall.main(username, password, sshkey, server, port, cmdstring)


logging = False if logfile == "" else True
if logging:
    if not os.path.isfile(logfile):
        try:
            write_log("Created log file")
        except:
            print("[!] Error - Could not create log file at '%s'" % logfile)
            raise
            sys.exit()

if not len(sys.argv) == 2:
    printhelp()
    sys.exit()

if server == "" or username == "" or firewallGroupName == "":
    print("[!] Open this script in a text editor and enter an applicable SSH server address, user and firewall group name.")
    sys.exit()
if sshkey == "":
    if password == "":
        password = getpass.getpass('(%s@%s) Enter password: ' % (username, server))


today = datetime.date.today()
blockip = sys.argv[1]
if blockip == "-h" or blockip == "--help":
    printhelp()
elif not isip(blockip):
    print("[!] Error - invalid IP address '%s'" % blockip)
    write_log("Error - Invalid IP address '%s'" % blockip)
    sys.exit()
objname = "AUTOADD_%s_%s" % (blockip, today)

if alreadyBlocked(blockip):
    print("[-] IP '%s' is already in group '%s'. No actions taken." % (blockip, firewallGroupName))
    write_log("IP '%s' is already in group '%s'. No actions taken." % (blockip, firewallGroupName))
else:
    print("[-] Adding IP '%s' to '%s'..." % (blockip, firewallGroupName))
    addip()
    print("[-] Done")
    write_log("Added IP '%s' to firewall group '%s'" % (blockip, firewallGroupName))







