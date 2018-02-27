#!/usr/bin/python


### This is a central location for reusable functions


import sys
import os
import re
import datetime
import struct
import socket
import getpass
import subprocess
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText


# tries to get the file path for the configuration file
def get_config_path():
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    path = scriptdir + "/config"
    if os.path.isfile(path):
        return path
    else:
        print("\033[91m[!]\033[0m ERROR could not find configuration file in %s" % scriptdir)
        sys.exit()

# parse the configuration file to get variable values
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

# check if a configuration value is "on" or "yes" (if binary)
def is_config_enabled(path, param):
    config = read_config(path, param).lower()
    return True if config in ("on", "yes", "y") else False

# make a date look nice
def format_date(date):
    return date.strftime('%m-%d-%Y %H:%M:%S')

# if logging is enabled in the configuration file, this function writes to the log file
def write_log(line, logging, logfile):
    if logging:
        with open(logfile, 'a') as f:
            f.write("%s %s\n" % (format_date(datetime.datetime.now()), line))

# checks if input is a valid IP address
def isip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

# CIDR format compatibility - checks if an IP is in a network
def addressInNetwork(ip, net_n_bits):
    ipaddr = struct.unpack('<L', socket.inet_aton(ip))[0]
    net, bits = net_n_bits.split('/')
    netaddr = struct.unpack('<L', socket.inet_aton(net))[0]
    netmask = ((1L << int(bits)) - 1)
    return ipaddr & netmask == netaddr & netmask

# Check if an IP is in the whitelist
def in_whitelist(ip, whitelist):
    # iterate over each of the addresses listed in the whitelist
    for address in whitelist:
        if "/" in address:
            # if a slash is in the address, assume it is a network segment in CIDR notation
            if addressInNetwork(ip, address):
                return True
        else:
            # if there's no slash, assume it is a single IP address & compare directly
            if ip == address:
                return True
    return False

# When sending email notifications, this function grabs the country code for an IP address
def get_country(ip):
    # Using "ipinfo.io" free API to get country info
    url = "ipinfo.io/" + ip + "/geo"
    cmd = "curl -s " + url
    try:
        # subprocess command should be compatible in Python 2.x and 3.x
        proc = subprocess.Popen(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)
        (curlresponse, err) = proc.communicate()
        # the expected ipinfo response is in JSON format
        data = json.loads(curlresponse)
        country = data["country"]
    except:
        # if the curl request fails, just make the country code blank
        country = ""
    return country

# if email is enabled in the configuration file, this is the function that actually sends the email
def send_email(subject, content, mailfrom, mailuser, mailpass, mailto, mailserver, mailport):
    msg = MIMEMultipart()
    msg['From'] = mailfrom
    msg['To'] = mailto
    msg['Subject'] = subject
    msg.attach(MIMEText(content))

    server = smtplib.SMTP("%s" % (mailserver), mailport)
    server.ehlo()
    if mailuser != "":
        server.starttls()
        server.ehlo()
        server.login(mailuser, mailpass)

    # send the mail
    server.sendmail(mailfrom, mailto, msg.as_string())
    server.close()

# checks to see if there are any errors in the configuration file
def check_config(serverlist, username, password, sshkey, port, fwgroup, whitelist, logfile, sendemail, mailfrom, mailuser, mailpass, mailto, mailserver, mailport):
    if not serverlist or not username or not fwgroup:
        print("[!] Open 'blockip.conf' in a text editor and enter an applicable SSH server address, username, and firirewall group name.")
        sys.exit()
    if sshkey == "":
        if password == "":
            try:
                password = getpass.getpass('Enter password for user "%s": ' % username)
            except KeyboardInterrupt:
                sys.exit()

# makes sure the log file exists, if applicable
def init_log(logging, logfile):
    if logging:
        if not os.path.isfile(logfile):
            try:
                write_log("Created log file", logging)
            except:
                print("[!] Error - Could not create log file at '%s'" % logfile)
                raise
                sys.exit()