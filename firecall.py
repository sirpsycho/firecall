#!/usr/bin/python

import sys
import optparse
import getpass
from time import sleep
try:
    import paramiko
except ImportError:
    print("[!] Could not find dependency 'paramiko'.  Try 'pip install paramiko'")
    sys.exit()


# Get Options
parser = optparse.OptionParser()

parser.add_option('-u', '--username',
                  dest="username",
                  default="",
                  help='SSH username',
                 )
parser.add_option('-p', '--pass',
                  dest="password",
                  default="",
                  help='SSH password (leave blank to be prompted)',
                 )
parser.add_option('-k', '--key',
                  dest="sshkey",
                  default="",
                  help='SSH private key location (ex. /home/user/.ssh/id_rsa)',
                 )
parser.add_option('-s', '--server',
                  dest="server",
                  default="",
                  help='SSH server address',
                 )
parser.add_option('-P', '--port',
                  dest="port",
                  default=22,
                  help='SSH port',
                 )
parser.add_option('-c', '--cmdstring',
                  dest="cmdstring",
                  default="",
                  help='Command(s) to run on SSH server',
                 )
parser.add_option('-d', '--debug',
                  dest="debug",
                  default=False,
                  action="store_true",
                  help='Show verbose output, including commands & response',
                 )
parser.set_usage("Usage: python firecall.py -u <user> -s <server> -c <commandstring>")
options, remainder = parser.parse_args()

# set variables defined in options menu
username = options.username
password = options.password
sshkey = options.sshkey
server = options.server
try:
    port = int(options.port)
except:
    print("[!] Invalid port")
    sys.exit()
cmdstring = options.cmdstring
debug = options.debug

# this command disables paging on the firewall, so that output is not cut off
def disable_paging(shell):
    shell.sendall("terminal pager 0\n")
    sleep(0.1)
    output = shell.recv(65535)
    shell.sendall("\n")

# this is the main function that actually sends the command to the firewall
def exec_cmd(shell, cmd):
    shell.sendall(cmd + '\n')
    sleep(1)
    output = shell.recv(65535)
    return output

def main(username, password, sshkey, server, port, cmdstring):
    # make sure all the variables are configured correctly
    if cmdstring == "":
        print("[!] Provide command(s) to run with -c option")
        sys.exit()
    if server == "":
        server = raw_input('Enter SSH server address: ')
        if server == "": sys.exit()
    if username == "":
        username = raw_input('Enter SSH username: ')
        if username == "": sys.exit()
    if sshkey == "":
        usekey = False
        if password == "":
            password = getpass.getpass('(%s@%s) Enter password: ' % (username, server))
    else:
        usekey = True

    ssh = paramiko.SSHClient()
    # auto-accept the "save new SSH key???" prompt
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # initiate SSH connection
    try:
        if usekey:
            # Using SSH key
            ssh.connect(server, port=port, username=username, key_filename=sshkey, look_for_keys=False, allow_agent=False)
        else:
            # Using SSH password
            ssh.connect(server, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
        if debug: print("[-] Connected to '%s'" % server)
    except paramiko.ssh_exception.AuthenticationException:
        errmsg = "Username or password incorrect on '%s'" % server
        return "", errmsg
    except paramiko.ssh_exception.NoValidConnectionsError:
        errmsg = "Unable to connect to '%s' on port '%s'" % (server, port)
        return "", errmsg

    sshshell = ssh.invoke_shell()
    sleep(0.5)

    # get enable mode
    sshshell.sendall("\n")
    sleep(0.1)
    prompt = sshshell.recv(256)
    if "> " in prompt:
        # Low privilege mode detected - try enable command
        sshshell.sendall("enable\n\n\n\n\n")
        sleep(0.1)
        output = sshshell.recv(1024)
        sshshell.sendall("\n")
        sleep(0.1)
        prompt = sshshell.recv(1024)
        if "> " in prompt:
            errmsg = "Could not enter enable mode on '%s'" % server
            return "", errmsg

    # disable paging on FW
    disable_paging(sshshell)


    if debug: print("[-] Sending command string...\n")
    output = exec_cmd(sshshell, cmdstring)
    return output, ""

if __name__ == '__main__':
    output, errmsg = main(username, password, sshkey, server, port, cmdstring)
    if errmsg:
        print("-%s-" % errmsg)
    else:
        print(output)