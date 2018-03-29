#!/usr/bin/python

from core import *
import firecall
import sys
import os
import datetime


def printhelp():
    print("Usage: python blockip.py <ip-address>\n\nEnter an IP to block at the firewall level.  Before running this script, make sure to edit & configure 'config' file.\n")

# Check to see if the IP is already blocked
def alreadyBlocked(blockip, server):
    cmdstring = "sh run object-group id %s | inc _%s_" % (fwgroup, blockip)
    output, errmsg = firecall.main(username, password, sshkey, server, port, cmdstring)
    if "AUTOADD_%s_" % blockip in output:
        return True
    else:
        return False

# Send commands to the firewall to add the input IP to the firewall group specified in 'config'
def addip(blockip, server):
    objname = "AUTOADD_%s_%s" % (blockip, today)
    desc = "Added by '%s' via script on %s" % (username, today)
    cmdstring = """configure terminal
object network %s
host %s
description %s
object-group network %s
network-object object %s
write mem""" % (objname, blockip, desc, fwgroup, objname)
    return firecall.main(username, password, sshkey, server, port, cmdstring)


def main(blockip):
    # Set these variables as global so that they can be used across functions
    global serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport, today

    # get the path for the configuration file
    path = get_config_path()

    # Read variables in from the configuration file
    serverlist = read_config(path, "SERVER_LIST").split(',')
    username = read_config(path, "SSH_USERNAME")
    password = read_config(path, "SSH_PASSWORD")
    sshkey = read_config(path, "SSH_KEY")
    port = read_config(path, "SSH_PORT")
    fwgroup = read_config(path, "FIREWALL_GROUP_NAME")
    whitelist = read_config(path, "WHITELIST_IPS").split(',')
    logfile = read_config(path, "LOG_FILE")
    logging = False if logfile == "" else True

    sendemail = is_config_enabled(path, "SEND_EMAIL_ON_BLOCK")
    mailfrom = read_config(path, "EMAIL_FROM")
    mailuser = read_config(path, "EMAIL_USERNAME")
    mailpass = read_config(path, "EMAIL_PASSWORD")
    mailto = read_config(path, "EMAIL_TO")
    mailserver = read_config(path, "EMAIL_SERVER")
    mailport = read_config(path, "EMAIL_PORT")

    today = datetime.date.today()

    # if logging is enabled, make sure the log file is accessible
    init_log(logging, logfile)

    # make sure there are no errors in the configuration file
    serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport = check_config(serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport)

    # display help info
    if blockip == "-h" or blockip == "--help":
        printhelp()
    # make sure the input IP is a valid IP address
    elif not isip(blockip):
        print("[!] Error - invalid IP address '%s'" % blockip)
        write_log("Error - Invalid IP address '%s'" % blockip, logging, logfile)
        sys.exit()
    # make sure the input IP is not whitelisted in the configuration file
    elif in_whitelist(blockip, whitelist):
        print("[!] IP '%s' is whitelisted in 'config'. No actions taken." % blockip)
        write_log("IP '%s' is whitelisted in 'config'. No actions taken." % blockip, logging, logfile)
        sys.exit()
    # create the object name to be used in the firewall
    objname = "AUTOADD_%s_%s" % (blockip, today)

    # if there are multiple firewalls, block the IP for each one
    for server in serverlist:
        if alreadyBlocked(blockip, server):
            print("[-] (%s) IP '%s' is already in group '%s'. No actions taken." % (server, blockip, fwgroup))
            write_log("(%s) IP '%s' is already in group '%s'. No actions taken." % (server, blockip, fwgroup), logging, logfile)
        else:
            output, errmsg = addip(blockip, server)
# Uncomment to debug firewall commands:
#            print(output)
            if errmsg:
                print("[!] (%s) Error: %s" % (server, errmsg))
                write_log("(%s) Error: %s" % (server, errmsg), logging, logfile)
            # if the commands ran, this string should be in the command output (after running 'write mem')
            elif "Building configuration" in output:
                print("[-] (%s) Added IP '%s' to firewall group '%s'" % (server, blockip, fwgroup))
                write_log("(%s) Added IP '%s' to firewall group '%s'" % (server, blockip, fwgroup), logging, logfile)
            # the script was able to connect to the firewall, but the output was unexpected
            else:
                print("[!] (%s) Error: Connection successful, but an error occurred when running commands" % server)
                write_log("(%s) Error: Connection successful, but an error occurred when running commands" % server, logging, logfile)
    # if email is enabled in the configuration file...
    if sendemail:
        # grab country code for IP
        country = get_country(blockip)
        # compose notification email
        subject = "Automated Firewall Block Notification"
        content = "Blocked IP: %s (%s)\n\n" % (blockip, country)
        content += "Time of block: %s\n\n" % format_date(datetime.datetime.now())
        content += "Blocked on the following firewall(s):\n"
        for server in serverlist:
            content += "    %s\n" % server
        content += "\nDetails:\nThe attacking IP address referenced above exceeded the connection threshold on a honeypot, resulting in an automated block on the above-referenced firewall(s)."

        print("[-] Sending notification email...")
        try:
            send_email(subject, content, mailfrom, mailuser, mailpass, mailto, mailserver, mailport)
            print("[-] Successfully sent notification email")
            write_log("Successfully sent notification email", logging, logfile)
        except:
            print("[!] Notification email failed to send.  Details:\n\n")
            raise

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        printhelp()
        sys.exit()
    blockip = sys.argv[1]
    main(blockip)
