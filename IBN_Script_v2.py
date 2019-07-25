#
# Copyright (c) 2018  Krishna Kotha <krkotha@cisco.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# PURPOSE of this SCRIPT
# The purpose of this script is to Simplify IBN Migration. 
# Learning existing Customer network deployments and leveraging/using Automation
# capabilities available on the Cat9k platforms. Our solution helps them to migrate
# into a new SDA network in a cost-effective, less/no impact to the business 
#operations and, in an automated manner.
#
# importing necessary modules
import os
import sys
import time
import difflib
from datetime import datetime
from time import strptime
from time import mktime
import smtplib
import shutil
import sys, paramiko


def hosts_file():
    """
    This Function is to get the device details like IP, username, password
    :param hosts.txt:
    :return:
    """
    # read the hosts.txt file from the same directory
    ip_file=open('hosts.txt','r')
    ip_file.seek(0)
    ip_list=ip_file.readlines()

    #closing the file
    ip_file.close()

    return ip_list


def configure_cmds(output_list,interface):
    """
    This function is to configure the fabric commands that already saved in the cmd_file in same directory
    :param output_list and interface
    """

    print ("\nConfiguring the %s" % output_list[interface-1])
    
    connection.send("configure terminal \n")
    connection.send("int gi 3/0/1 \n")
    connection.send("shut\n")
    connection.send(" %s \n" % output_list[interface-1])
    time.sleep(2)

    # execute shut down on the interface 
    connection.send("shut\n")
    time.sleep(1)

    print ("\nIOT device is discovered and connected to the %s" % output_list[interface-1])

    print ("\nConfiguring the fabric commands for %s" % output_list[interface-1])
    
    # read the fabric commands from cmd_file 
    fabric_cmds_file = open('interface_cmd.txt', 'r')
    fabric_cmds_file.seek(0)

    # for loop to execute each command in the cmd file
    for each_cmd in fabric_cmds_file.readlines():
        connection.send(each_cmd + '\n')
        time.sleep(1)
    
    fabric_cmds_file.close()
    
    # execuring no shut on the interface
    connection.send("no shut\n")
    time.sleep(1)
    connection.send("end\n")


def global_cmds():
    """
    This function is to configure the fabric commands that already saved in the cmd_file in same directory
    :param output_list and interface
    """

    print ("\nConfiguring the routing and switching paths")
    
    connection.send("configure terminal \n")
    
    # read the fabric commands from cmd_file 
    global_cmds_file = open('cmd_file.txt', 'r')
    global_cmds_file.seek(0)

    # for loop to execute each command in the cmd file
    for each_cmd in global_cmds_file.readlines():
        connection.send(each_cmd + '\n')
        time.sleep(1)
    
    global_cmds_file.close()

    connection.send("end\n")

def delete_interface(output_list,interface):
    """
    This function is to remove all the existing legacy configuration on the device
    :param output_list and interface
    """
    print ("Deleting the existing legacy configuration on the %s" % output_list[interface-1])
    connection.send("configure terminal \n")
    
    # executing default on the interface
    connection.send("default %s \n" % output_list[interface-1])
    time.sleep(1)
    connection.send("end\n")


# main code:
if __name__ == '__main__':

    try:

        print ("""****************************************************************

    Simplifying IBN Migration by learning existing Customer network 
    deployments and leveraging/using Automation capabilities. This 
    solution helps customers to migrate into a new SDA network 
    in a cost-effective, less/no impact to the business operations 
    in an automated manner.

******************************************************************\n\n""")
        
        # reading all the device paramaters from the hosts.txt
        host_list = hosts_file()

        # seperate the ip address from the hosts file
        ip_list_0 = host_list[0].split(':')
        ip_address=ip_list_0[1].rstrip("\n")

        #Checking octets            
        ip_octets = ip_address.split('.')

        if (len(ip_octets) == 4) and (1 <= int(ip_octets[0]) <= 223) and (int(ip_octets[0]) != 127) and (int(ip_octets[0]) != 169 or int(ip_octets[1]) != 254) and (0 <= int(ip_octets[1]) <= 255 and 0 <= int(ip_octets[2]) <= 255 and 0 <= int(ip_octets[3]) <= 255):
            pass
            
        else:
            print("\nThe IP address is INVALID! Please verify \n")

        # seperate the username from the hosts file
        ip_list_1 = host_list[1].split(':')
        username=ip_list_1[1].rstrip("\n")

        # seperate the password from the hosts file
        ip_list_2 = host_list[2].split(':')
        password=ip_list_2[1].rstrip("\n")

        ip_list_3 = host_list[3].split(':')
        port=ip_list_3[1].rstrip("\n")

        #Open SSHv2 connection to the device
        #Logging into device
        session=paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # connect to the device using username and password 
        session.connect(ip_address, username=username,password=password, look_for_keys=False, allow_agent=False)
        
        # start an interactive shell session on the router
        connection = session.invoke_shell()

        connection.send("enable\n")
        connection.send("terminal length 0\n")
        time.sleep(1)
        
        # executing show run on the device and saving the output
        connection.send("show run \n")
        time.sleep(5)
        router_output = connection.recv(100000)
        #print router_output
        
        # separating the output to a list
        strip_output=router_output.strip(" ")
        time.sleep(1)
        #print strip_output

        output_list=strip_output.split('\r\n')
        time.sleep(1)
        #print output_list

        interface=output_list.index(' description Fabric_Migration')

        # deleting the interface configuration by calling the function
        delete_interface(output_list,interface)
        
        # configuring global commands calling the function
        global_cmds()

        # configuring the interface with fabric commands by calling the function
        configure_cmds(output_list,interface)

        print("\n********* Ta da...Now device has migrated from existing legacy network to SDA Fabric*********\n\n")
        session.close()


    except paramiko.AuthenticationException:
        # raises authentication error

        print("* Invalid username or password :( \n* Please check the username/password file or the device configuration.")
        print("* Closing program... Bye!")