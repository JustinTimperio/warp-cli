#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.3
from global_defuns import * 
import subprocess, argparse

############
## Defs and Vars
########
default_options = "-num_ports=8 -max_mbytes_per_sec=-1 -progress_report_interval_millis=5000"

############
## CLI Wrapper Tool
########
def ship(src_ssh_alias, src_path, recv_ssh_alias, recv_path):
    os.system("ssh " + recv_ssh_alias + " wdt " + default_options + " -directory " + recv_path + " | ssh " + src_ssh_alias + " wdt " + default_options + " -directory " + src_path + " -")

def push(src_path, recv_ssh_alias, recv_path):
    os.system("ssh " + recv_ssh_alias + " wdt " + default_options + " -directory " + recv_path + " | wdt " + default_options + " -directory " + src_path + " -")

def fetch(src_ssh_alias, src_path, recv_path):
    os.system("wdt " + default_options + " -directory " + recv_path + " | ssh " + src_ssh_alias + " wdt " + default_options + " -directory " + src_path + " -")

############
## Start WDT Daemon
########
def start_recv_daemon(recv_path='/var/app/inbound'):
    import getpass 
    import datetime
    receiver_cmd = ("wdt -overwrite -max_mbytes_per_sec=-1 -progress_report_interval_millis=-1 -directory " + recv_path)
    receiver_process = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, shell=True)
    connection_url = str(receiver_process.stdout.readline().strip())[1:] 
    meta_data = str("Recvier daemon started by " + getpass.getuser() + " in " + recv_path + " at " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection_file = [meta_data, connection_url]
    export_path = ("/var/app/wdt/pool/" + getpass.getuser() + "_" + str(datetime.datetime.now().strftime("%m_%d-%H:%M_%S")) + ".txt")
    touch(export_path, 'u')
    export_list(export_path, connection_file)
    return export_path

############
## Argument Parser
########
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A quick and simple wrapper for the WDT CLI Tool. For additional support use 'wdt --help | less'")
    parser.add_argument("-s", "--ship", help="Warp a remote directory to another remote directory. Options: src_ssh_alias, src_path, recv_ssh_alias, recv_path")
    parser.add_argument("-p", "--push", help="Warp a local directory to a remote directory. Options: src_path, recv_ssh_alias, recv_path")
    parser.add_argument("-f", "--fetch", help="Warp a remote directory to a local directory. Options: src_ssh_alias, src_path, recv_path")
    parser.add_argument("-d", "--daemon", help="Start a daemon on a directory. Returns a connection url to /var/app/wdt. Options: recv_path")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    arguments = parser.parse_args()
    main(arguments)

