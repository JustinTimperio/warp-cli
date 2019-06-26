#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.2
from global_defuns import * 
import os, sys, subprocess, argparse

############
## Setup WDT
########
def setup_wdt():
    base_dir = ("/var/app/wdt")
    ## setup dirs
    mkdir('/var/app', 'r')
    mkdir(base_dir, 'r')
    mkdir(base_dir + '/pool', 'r')
    mkdir(base_dir + '/inbound', 'r')
    mkdir(base_dir + '/outbound', 'r')
    open_permissions('/var/app')
    ## fetch and update all packages needed for WDT - https://github.com/facebook/wdt/blob/master/build/BUILD.md 
    aurman_install('cmake jemalloc wdt-git')

############
## CLI Wrapper Tool
########
def warp_from_to(src_ssh_alias, src_path, recv_ssh_alias, recv_path):
    os.system('ssh ' + recv_ssh_alias + " wdt -num_ports=8 -max_mbytes_per_sec=-1 -directory " + recv_path + " | ssh " + src_ssh_alias + " wdt -max_mbytes_per_sec=-1 -num_ports=16 -directory " + src_path + " -" )

def warp_to(src_path, recv_ssh_alias, recv_path):
    os.system('ssh ' + recv_ssh_alias + " wdt -num_ports=8 -max_mbytes_per_sec=-1 -directory " + recv_path + " | wdt -max_mbytes_per_sec=-1 -num_ports=16 -directory " + src_path + " -" )

def warp_from(src_ssh_alias, src_path, recv_path):
    os.system("wdt -num_ports=8 -max_mbytes_per_sec=-1 -directory " + recv_path + " | ssh " + src_ssh_alias + " wdt -max_mbytes_per_sec=-1 -num_ports=16 -directory " + src_path + " -" )

############
## Start WDT Daemons
########
def start_recv_daemon(recv_path='/var/app/inbound'):
    import getpass 
    import datetime
    receiver_cmd = ("wdt -overwrite -max_mbytes_per_sec=-1 -progress_report_interval_millis=-1 -directory " + recv_path)
    #  receiver_cmd = ("wdt -run_as_daemon -overwrite -max_mbytes_per_sec=-1 -progress_report_interval_millis=1200 -directory " + recv_path)
    receiver_process = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, shell=True)
    connection_url = str(receiver_process.stdout.readline().strip())[1:] 
    meta_data = str("Recvier daemon started by " + getpass.getuser() + " in " + recv_path + " at " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    connection_file = [meta_data, connection_url]
    export_path = ('/var/app/wdt/pool/' + getpass.getuser() + "_" + str(datetime.datetime.now().strftime("%m_%d-%H:%M_%S")) + '.txt')
    touch(export_path, 'u')
    export_list(export_path, connection_file)
    return export_path

start_recv_daemon()

############
## Argument Parser
###########
parser = argparse.ArgumentParser(description="A quick and simple wrapper for the WDT CLI Tool. For additional support use 'wdt --help | less'")
parser.add_argument("-ft", "--from_to", help="Warp a remote directory to a remote directory. Options: src_ssh_alias, src_path, recv_ssh_alias, recv_path")
parser.add_argument("-t", "--to", help="Warp a local directory to a remote directory. Options: src_path, recv_ssh_alias, recv_path")
parser.add_argument("-f", "--from", help="Warp a remote directory to a local directory. Options: src_ssh_alias, src_path, recv_path")
parser.add_argument("-d", "--daemon", help="Start a daemon on a directory. Returns a connection url to /var/app/wdt. Options: recv_path")
arguments = parser.parse_args()
