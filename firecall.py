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

username = options.username
password = options.password
server = options.server
try:
    port = int(options.port)
except:
    print("[!] Invalid port")
    sys.exit()
cmdstring = options.cmdstring
debug = options.debug


def disable_paging(shell):
    shell.sendall("terminal pager 0\n")
    sleep(0.1)
    output = shell.recv(65535)
    shell.sendall("\n")

def exec_cmd(shell, cmd):
    shell.sendall(cmd + '\n')
    sleep(1)
    output = shell.recv(65535)
    return output

def main(username, password, server, port, cmdstring):
    if cmdstring == "":
        print("[!] Provide command(s) to run with -c option")
        sys.exit()
    if server == "":
        server = raw_input('Enter SSH server address: ')
        if server == "": sys.exit()
    if username == "":
        username = raw_input('Enter SSH username: ')
        if username == "": sys.exit()
    if password == "":
        password = getpass.getpass('(%s@%s) Enter password: ' % (username, server))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(server, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
        if debug: print("[-] Connected to '%s'" % server)
    except paramiko.ssh_exception.AuthenticationException:
        print("[!] Error: Username or password incorrect")
        sys.exit()

    sshshell = ssh.invoke_shell()
    sleep(0.5)

    # disable paging on FW
    disable_paging(sshshell)

    if debug: print("[-] Sending command string...\n")
    output = exec_cmd(sshshell, cmdstring)
    return output

if __name__ == '__main__':
    output = main(username, password, server, port, cmdstring)
    print(output)







