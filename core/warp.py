#! /usr/bin/env python3
#### WDT Wrapper - https://github.com/facebook/wdt
version = '2.1.4'
from python_scripts import *
import sys, argparse

############
## WDT CLI Wrapper
########
def ship(src_ssh, src_path, recv_ssh, recv_path, options):
    recv_cmd = ("ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path)
    run_cmd = subprocess.Popen(recv_cmd, stdout=subprocess.PIPE, shell=True)
    wdt_url = str(run_cmd.stdout.readline().strip())[1:]
    os.system("echo " + wdt_url + " | ssh " + src_ssh + ' wdt' + options + " -directory " + src_path + ' -')

def push(src_path, recv_ssh, recv_path, options):
    cmd = ("ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path +
              " | wdt" + options + " -directory " + src_path + " -")
    ### check if gen_macro
    if gen_macro_flg is False:
        os.system(cmd)
    elif gen_macro_flg is True:
        gen_macro(cmd, escape_bash(args.gen_macro))
    else:
        sys.exit('Critical Error: gen_macro_flg Not Set!')

def fetch(src_ssh, src_path, recv_path, options):
    cmd = ("wdt" + options + " -directory " + recv_path +
              " | ssh " + src_ssh + " wdt" + options + " -directory " + src_path + " -")
    ### check if gen_macro
    if gen_macro_flg == False:
        os.system(cmd)
    elif gen_macro_flg == True:
        gen_macro(cmd, escape_bash(args.gen_macro))
    else:
        sys.exit('Critical Error: gen_macro_flg Not Set!')

############
## Options
########
def build_options(ports, mbytes, interval, overwrite, custom_parms):
    num_ports = " -num_ports=" + str(args.threads)
    avg_mbytes = " -avg_mbytes_per_sec=" + str(args.throttle_speed)
    report_interval = " -progress_report_interval_millis=" + str(args.report_interval)
    overwrite = " -overwrite=" + str(args.overwrite).lower()
    sym_links = " -follow_symlinks=" + str(args.follow_sym).lower()
    options = (num_ports + avg_mbytes + report_interval + overwrite + custom_parms)
    return options

############
## Macro Generator
########
def gen_macro(cmd, macro_name):
    os.system("echo '" + cmd + "' > " + base_dir + "/macros/" + macro_name)
    print("Macro Successfully Generated!")

def run_macro(macro_name):
    macro_path = (base_dir + '/macros/' + macro_name)
    os.system('cat ' + macro_path + " | bash")
    print('Transfer Complete!')

############
## Start WDT Daemon
########
def start_recv_daemon(recv_path, options):
    from getpass import getuser as user
    from datetime import datetime
    recv_cmd = ("wdt -run_as_daemon=true" + options + " -directory " + recv_path)
    run_cmd = subprocess.Popen(recv_cmd, stdout=subprocess.PIPE, shell=True)
    wdt_url = str(run_cmd.stdout.readline().strip())[1:]
    
    ## generate a connection file containing meta data about the daemon
    meta_data = str("Recvier daemon started by " + user() + " in " + recv_path + " at " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    export_path = base_dir + "/pool/" + user() + "_" + str(datetime.now().strftime("%m_%d-%H:%M_%S")) + ".txt"
    os.system('cat > ' + export_path)
    export_list(export_path, [meta_data, wdt_url])
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
parser.add_argument("-ts", "--throttle_speed", default="-1", metavar='INT', help=" Throttle the transfer to an average mbytes per second.")
parser.add_argument("-ow", "--overwrite", action='store_true', help="Allow the receiver to overwrite existing files in a directory.")
parser.add_argument("-sym", "--follow_sym", action='store_true', help="Let WDT follow symlinks during transfer.")
parser.add_argument("-cp", "--custom_parms", default="", metavar="-CUSTOM_PARM value", help="Inject any additional parameters available in `wdt --help`.")
### utilities
parser.add_argument("-d", "--daemon", metavar='/DIR/FOR/DAEMON', help="Start a receiver daemon on a directory. Returns a connection url to ~/warp-cli/macros.")
parser.add_argument("-m", "--macro", metavar='MACRO_NAME', help="Execute a macro by name from ~/warp-cli/macros.")
parser.add_argument("-gm", "--gen_macro", metavar='MACRO_NAME', help="Generate a new macro. This will overwrite a old macro if named the same.")
parser.add_argument("-v", "--version", action='store_true', help="List Warp-CLI, WDT, and FOLLY Version.")
### install commands
parser.add_argument("-in", "--install", action='store_true', help="Attempt an automated install of WDT and dependencies.")
parser.add_argument("-ir", "--install_remote", nargs=2, metavar='SSH.ALIAS /DIR/TO/INSTALL', help="Attempt an automated install of WDT and dependencies on a remote machine.")
parser.add_argument("-dev", "--dev_install", action='store_true', help="Install the Dev branch of Warp-CLI during a remote install. For Dev use only!")
parser.add_argument("-rm", "--uninstall", action='store_true', help="Remove Warp-CLI and config files.")

############
## Trigger Core Args
########
args = parser.parse_args()
base_dir = os.path.dirname(os.path.realpath(__file__))[:-5]
gen_macro_flg = False

if args.gen_macro:
    if args.ship:
        sys.exit('Macros for --ship Commands Are NOT Yet Supported!')
    else:
        gen_macro_flg = True

if args.version:
    print('Warp-CLI Version ' + version)
    if os.path.exists(base_dir + '/build/folly/.git/HEAD'):
        os.system('echo "FOLLY VERSION" `cd ' + base_dir + '/build/folly && git describe`')

if args.fetch:
    fetch(args.fetch[0], escape_bash(args.fetch[1]), escape_bash(args.fetch[2]),
        build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

elif args.push:
    push(escape_bash(args.push[0]), args.push[1], escape_bash(args.push[2]), 
        build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

elif args.ship:
    ship(args.ship[0], escape_bash(args.ship[1]), args.ship[2], escape_bash(args.ship[3]),
        build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

### trigger utilities
elif args.daemon:
    start_recv_daemon(escape_bash(args.daemon), 
        build_options(args.threads, args.throttle_speed, args.report_interval, args.overwrite, args.custom_parms))

elif args.macro:
    if not os.path.exists(base_dir + '/macros/' + args.macro):
        sys.exit(args.macro + " Was NOT Found in " + base_dir + "/macros/")
    else:
        run_macro(escape_bash(args.macro))

elif args.install == True:
    from setup import *
    setup_warp(base_dir)

elif args.install_remote:
    from setup import *
    setup_warp_remote(args.install_remote[0], args.install_remote[1], args.dev_install)

elif args.uninstall == True:
    from setup import *
    uninstall_warp(base_dir)
