#!/usr/bin/python

from core import *
import firecall
import sys
import os
import datetime


def printhelp():
    print("Usage: python removeip.py <ip-address>\n\nEnter an IP to remove from firewall(s).  Before running, make sure to edit & configure 'config' file\n")

# if the IP is already blocked, get the name of the object defined on the firewall
def get_objname(ip, server):
    cmdstring = "sh run object-group id %s" % fwgroup
    output, errmsg = firecall.main(username, password, sshkey, server, port, cmdstring)
    string = "AUTOADD_%s_" % ip
    if string in output:
        # split output on all whitespace
        for string in output.split():
            if ip in string:
                return str(string)
    else:
        # if the IP is not found in the firewall object list, just return False
        return False

# send commands to the firewall to remove the specified IP
def removeobject(objname, server):
    cmdstring = """configure terminal
object-group network Deny_All_Group
no network-object object %s
no object network %s
write mem""" % (objname, objname)
    return firecall.main(username, password, sshkey, server, port, cmdstring)


def main(ip):
    # Set these variables as global to be reused across functions
    global serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport, today

    # get the configuration file path
    path = get_config_path()

    # get the variables defined in the configuration file
    serverlist = read_config(path, "SERVER_LIST").split(',')
    username = read_config(path, "SSH_USERNAME")
    password = read_config(path, "SSH_PASSWORD")
    sshkey = read_config(path, "SSH_KEY")
    port = read_config(path, "SSH_PORT")
    fwgroup = read_config(path, "FIREWALL_GROUP_NAME")
    whitelist = read_config(path, "WHITELIST_IPS").split(',')
    logfile = read_config(path, "LOG_FILE")
    logging = False if logfile == "" else True

    sendemail = is_config_enabled(path, "SEND_EMAIL_ON_REMOVE")
    mailfrom = read_config(path, "EMAIL_FROM")
    mailuser = read_config(path, "EMAIL_USERNAME")
    mailpass = read_config(path, "EMAIL_PASSWORD")
    mailto = read_config(path, "EMAIL_TO")
    mailserver = read_config(path, "EMAIL_SERVER")
    mailport = read_config(path, "EMAIL_PORT")

    today = datetime.date.today()

    # if logging is enabled, make sure the log file is ready
    init_log(logging, logfile)
    # make sure the configuration file doesn't contain any errors
    serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport = check_config(serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport)

    if ip == "-h" or ip == "--help":
        printhelp()
    # make sure the input IP is a valid IP address
    elif not isip(ip):
        print("[!] Error - invalid IP address '%s'" % ip)
        write_log("Error - Invalid IP address '%s'" % ip, logging, logfile)
        sys.exit()

    # if there are multiple firewalls defined in the config file, remove the IP on each one of them
    for server in serverlist:
        # get the specific object name currently being used on the firewall
        objname = get_objname(ip, server)
        # if 'objname' is false, it means the IP wasn't found in the firewall config
        if not objname:
            print("[-] (%s) IP '%s' was not found in '%s'. No actions taken." % (server, ip, fwgroup))
            write_log("(%s) IP '%s' was not found in '%s'. No actions taken." % (server, ip, fwgroup), logging, logfile)
        else:
            output, errmsg = removeobject(objname, server)
# Uncomment this line to debug firewall commands/output:
#            print(output)
            if errmsg:
                print("[!] (%s) Error: %s" % (server, errmsg))
                write_log("(%s) Error: %s" % (server, errmsg), logging, logfile)
            # if the commands ran properly, this string should be in the output (after running 'write mem')
            elif "Building configuration" in output:
                print("[-] (%s) Successfully removed IP '%s' from firewall group '%s'" % (server, ip, fwgroup))
                write_log("(%s) Successfully removed IP '%s' from firewall group '%s'" % (server, ip, fwgroup), logging, logfile)
            # the connection to the firewall was successful, but the output was unexpected
            else:
                print("[!] (%s) Error: Connection successful, but an error occurred when running commands" % server)
                write_log("(%s) Error: Connection successful, but an error occurred when running commands" % server, logging, logfile)
    # If email notifications are defined in the configuration file, send an email
    if sendemail:
        # get the country code for the IP
        country = get_country(ip)
        # compose notification email
        subject = "Block Removal - Firewall Notification"
        content = "Block REMOVED for IP: %s (%s)\n\n" % (ip, country)
        content += "Time of block removal: %s\n\n" % format_date(datetime.datetime.now())
        content += "Block removed on the following firewall(s):\n"
        for server in serverlist:
            content += "    %s\n" % server
        content += "\nDetails:\nA request was sent to the above-referenced firewall(s) to remove a block for the IP '%s'." % ip

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
    ip = sys.argv[1]
    main(ip)