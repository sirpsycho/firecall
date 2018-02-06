#!/usr/bin/python

import firecall
import sys
import os
import re
import datetime
import socket
import getpass


def printhelp():
    print("Usage: python blockip.py <ip-address>\n\nEnter an IP to block on a firewall.  Before running, make sure to edit & configure 'blockip.conf.'\n")

def get_config_path():
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    path = scriptdir + "/blockip.conf"
    if os.path.isfile(path):
        return path
    else:
        print("\033[91m[!]\033[0m ERROR could not find configuration file in %s" % scriptdir)
        sys.exit()

def read_config(path, param):
    fileopen = open(path, "r")
    for line in fileopen:
        if not line.startswith("#"):
            match = re.search(param + "=", line)
            if match:
                line = line.rstrip()
                line = line.replace('"', "")
                line = line.replace(' ', "")
                line = line.split(param + "=")
                return line[1]
    print("\033[91m[!]\033[0m ERROR - %s not found in %s" % (param, path))
    sys.exit()

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

path = get_config_path()
server = read_config(path, "SERVER")
username = read_config(path, "SSH_USERNAME")
password = read_config(path, "SSH_PASSWORD")
sshkey = read_config(path, "SSH_KEY")
port = read_config(path, "SSH_PORT")
fwgroup = read_config(path, "FIREWALL_GROUP_NAME")
whitelistips = read_config(path, "WHITELIST_IPS")
logfile = read_config(path, "LOG_FILE")


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

if not server or not username or not fwgroup:
    print("[!] Open 'blockip.conf' in a text editor and enter an applicable SSH server address, username, and firewall group name.")
    sys.exit()
if sshkey == "":
    if password == "":
        password = getpass.getpass('(%s@%s) Enter password: ' % (username, server))
whitelist = []
if whitelistips:
    whitelist = whitelistips.split(',')

today = datetime.date.today()
blockip = sys.argv[1]
if blockip == "-h" or blockip == "--help":
    printhelp()
elif not isip(blockip):
    print("[!] Error - invalid IP address '%s'" % blockip)
    write_log("Error - Invalid IP address '%s'" % blockip)
    sys.exit()
elif blockip in whitelist:
    print("[!] IP '%s' is whitelisted in blockip.conf. No actions taken." % blockip)
    write_log("IP '%s' is whitelisted in blockip.conf. No actions taken." % blockip)
    sys.exit()
else:
    print("TEST - blocking ip.........jk")
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


