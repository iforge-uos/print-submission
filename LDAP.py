from ldap3 import Server, Connection, ALL, get_config_parameter, set_config_parameter
import re
import socket
import time

ip = "auth.shef.ac.uk"
port = 389
retry = 1
delay = 0
timeout = 1


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def checkHost(ip, port):
    ipup = False
    for i in range(retry):
        if isOpen(ip, port):
            ipup = True
            break
        else:
            time.sleep(delay)
    return ipup


def Lookup(source):
    server = Server(ip)
    conn = Connection(server)
    bind = conn.bind()
    Name = 0
    Email = 0

    m = re.match("([a-zA-Z]{2,3}\d{1,3}[a-zA-Z]{2,3})", source)
    if m:
        Type = "uid"
        searchterm = source

    o = re.match("\S+@sheffield.ac.uk", source)
    if o:
        source = source.split('@')[0]
    n = re.match("([a-zA-Z]+[0-9]$)", source)
    n2 = re.match("(^[a-zA-Z]+\.)", source)
    if n or n2:
        searchterm = source + "@sheffield.ac.uk"
        Type = "mail"

    try:
        # conn.search('dc=sheffield,dc=ac,dc=uk', '(&(objectclass=person)(mail=%s))'%(Email), attributes=['givenName','sn'])
        conn.search('dc=sheffield,dc=ac,dc=uk', '(&(objectclass=person)(%s=%s))' % (Type, searchterm),
                    attributes=['givenName', 'sn', 'mail'])
        result = conn.entries[0]
        LDAP_data[0] = str(result.givenName) + " " + str(result.sn)
        LDAP_data[1] = str(result.mail)
        if LDAP_data[1] == '[]':
            raise
        LDAP_data[2] = "Complete"
        return (LDAP_data)
    except Exception as e:
        print("The details you have entered dont seem to be valid")
        LDAP_data[2] = "error in the submitted information"
        return (LDAP_data)


def go(source):
    global LDAP_data
    LDAP_data = [0, 0, 0]

    if checkHost(ip, port):
        print(ip + " is available to connect")
        Lookup(source)
        return (LDAP_data)
    else:
        print("Can't connect to " + ip)
        LDAP_data[2] = "network error"

        return (LDAP_data)
