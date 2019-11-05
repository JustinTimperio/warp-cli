#! /usr/bin/python
#### WDT Wrapper for WDT - https://github.com/facebook/wdt
## Version 1.7
from global_defuns import *
import argparse

############
## WDT CLI Wrapper
########
def ship(src_ssh, src_path, recv_ssh, recv_path, options):
    receiver_cmd = ("ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path)
    receiver_process = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, shell=True)
    connection_url = str(receiver_process.stdout.readline().strip())[1:]
    sender_cmd = ("ssh " + src_ssh + " wdt" + options + "-connection_url=" + connection_url + " -directory " + src_path + " -")
    subprocess.Popen(sender_cmd, stdout=subprocess.PIPE, shell=True)

def push(src_path, recv_ssh, recv_path, options):
    cmd = ("ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path +
              " | wdt" + options + " -directory " + src_path + " -")
    ### check if gen_macro
    if gen_macro_flg is False:
        os.system(cmd)
    elif gen_macro_flg is True:
        gen_macro(cmd, args.gen_macro)
    else:
        sys.exit('Critical Error Executing the Warp!')

def fetch(src_ssh, src_path, recv_path, options):
    cmd = ("wdt" + options + " -directory " + recv_path +
              " | ssh " + src_ssh + " wdt" + options + " -directory " + src_path + " -")
    ### check if gen_macro
    if gen_macro_flg == False:
        os.system(cmd)
    elif gen_macro_flg == True:
        gen_macro(cmd, args.gen_macro)
    else:
        sys.exit('Critical Error Executing the Warp!')

############
## Options
########
def build_options(ports, mbytes, interval, overwrite, custom_parms):
    num_ports = " -num_ports=" + str(args.threads)
    avg_mbytes = " -avg_mbytes_per_sec=" + str(args.throttle_speed)
    report_interval = " -progress_report_interval_millis=" + str(args.report_interval)
    overwrite = " -overwrite=" + str(args.overwrite)
    options = (num_ports + avg_mbytes + report_interval + overwrite + custom_parms)
    return options

############
## Macro Generator
########
gen_macro_flg = False
def gen_macro(cmd, macro_name):
    os.system("echo '" + cmd + "' > " + os.getcwd() + "/macros/" + macro_name)
    print("Macro Successfully Generated!")

def run_macro(macro_name):
    macro_path = (os.getcwd() + '/macros/' + macro_name)
    os.system('cat ' + macro_path + " | bash")
    print('Transfer Complete!')

############
## Start WDT Daemon
########
def start_recv_daemon(recv_path=os.getcwd()+'/inbound'):
    import getpass, datetime
    receiver_cmd = ("wdt -run_as_daemon=true -overwrite=true -max_mbytes_per_sec=-1 -progress_report_interval_millis=-1 -directory " + recv_path)
    receiver_process = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, shell=True)
    connection_url = str(receiver_process.stdout.readline().strip())[1:]
    ## generate a connection file containing meta data about the daemon
    meta_data = str("Recvier daemon started by " + getpass.getuser() + " in " + recv_path + " at " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection_file = [meta_data, connection_url]
    export_path = (os.getcwd + "/pool/" + getpass.getuser() + "_" + str(datetime.datetime.now().strftime("%m_%d-%H:%M_%S")) + ".txt")
    os.system('cat > ' + export_path)
    export_list(export_path, connection_file)
    print(meta_data)
    return export_path

############
## Argument Parser
########
parser = argparse.ArgumentParser(description="A simple wrapper for the WDT CLI Tool.")
parser.add_argument("-s", "--ship", nargs=4, metavar=('SRC_SSH_ALIAS','SRC_PATH','RECV_SSH_ALIAS','RECV_SSH_ALIAS'), help="Warp a remote directory to another remote directory.")
parser.add_argument("-p", "--push", nargs=3, metavar=('SRC_PATH','RECV_SSH_ALIAS','RECV_PATH'), help="Warp a local directory to a remote directory.")
parser.add_argument("-f", "--fetch", nargs=3, metavar=('SRC_SSH_ALIAS','SRC_PATH','RECV_PATH'), help="Warp a remote directory to a local directory.")
### optional arguments
parser.add_argument("-tr", "--threads", default="8", metavar='INT', help="Set the number of threads/ports for WDT to use.")
parser.add_argument("-ri", "--report_interval", default="3000", metavar='INT', help="Update interval in milliseconds for transfer report updates.")
parser.add_argument("-ts", "--throttle_speed", default="110", metavar='INT', help=" Throttle the transfer to an average mbytes per second.")
parser.add_argument("-ow", "--overwrite", default="false", metavar='BOOL', help="Allow the receiver to overwrite existing files in a directory.")
parser.add_argument("-cp", "--custom_parms", nargs='*', default="", metavar="-CUSTOM_PARM value", help="Inject any additional parameters available in `wdt --help`.")
### utilities
parser.add_argument("-d", "--daemon", metavar='/DIR/FOR/DAEMON', help="Start a receiver daemon on a directory. Returns a connection url to ~/warp-cli/macros.")
parser.add_argument("-m", "--macro", metavar='MACRO_NAME', help="Execute a macro by name from ~/warp-cli/macros.")
parser.add_argument("-gm", "--gen_macro", metavar='MACRO_NAME', help="Generate a new macro. This will overwrite a old macro if named the same.")
parser.add_argument("-in", "--install", metavar='/DIR/TO/INSTALL', help="Attempt an automated install of WDT and dependencies.")
parser.add_argument("-rm", "--uninstall", metavar='/DIR/TO/UNINSTALL', help="Remove Warp-CLI and config files.")

############
## Trigger Core Args
########
args = parser.parse_args()
if args.gen_macro:
    if args.ship:
        sys.exit('Macros for --ship commands are NOT yet supported!')
    else:
        gen_macro_flg = True

if args.fetch:
    fetch(''.join(args.fetch[:-2]), ''.join(args.fetch[1:-1]),''.join(args.fetch[2:]),
          build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

if args.push:
    push(''.join(args.push[:-2]), ''.join(args.push[1:-1]), ''.join(args.push[2:]),
          build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

if args.ship:
    ship(''.join(args.ship[:-3]), ''.join(args.ship[1:-2]), ''.join(args.ship[2:-1]), ''.join(args.ship[3:]),
          build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

### trigger utilities
if args.daemon:
    start_recv_daemon(arg.daemon)

if args.macro:
    if os.path.exists(os.getcwd() + '/macros/' + args.macro):
        sys.exit(args.macro + " is not found in " + os.getcwd() + "/macros/")
    else:
        run_macro(args.macro)

if args.install:
    from setup import setup_warp
    setup_warp(args.install)
    sys.exit('Install Complete!')

if args.uninstall:
    from setup import uninstall_warp
    uninstall_warp(args.uninstall)
    sys.exit('Uninstall Complete!')
