#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.5
from global_defuns import * 
import argparse

############
## WDT CLI Wrapper
########
def ship(src_ssh, src_path, recv_ssh, recv_path):
    global cmd
    cmd = ("URL=`ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path + "` && " +
              "echo $URL | ssh " + src_ssh + " wdt" + options + " -directory " + src_path + " -")

def push(src_path, recv_ssh, recv_path):
    global cmd
    cmd = ("ssh " + recv_ssh + " wdt" + options + " -directory " + recv_path + 
              " | wdt" + options + " -directory " + src_path + " -")

def fetch(src_ssh, src_path, recv_path):
    global cmd
    cmd = ("wdt" + options + " -directory " + recv_path + 
              " | ssh " + src_ssh + " wdt" + options + " -directory " + src_path + " -")

def warp(cmd, gen_macro_flg=False, macro_name='default_name'):
    ### check if gen_macro
    if gen_macro_flg == False:
        os.system(cmd)
    elif gen_macro_flg == True:
        gen_macro(cmd, macro_name)
    else:
        sys.exit('Critical Error Executing the Warp!')

############
## Macro Generater
########
def gen_macro(cmd, macro_name):
    os.system("echo '" + cmd + "' > /var/app/warp-cli/macros/" + macro_name)

def run_macro(macro_name):
    macro_list = ('/var/app/warp-cli/macros/' + macro_name)
    os.system('cat ' + macro_list + " | bash")

############
## Start WDT Daemon
########
def start_recv_daemon(recv_path='/var/app/warp-cli/inbound'):
    import getpass, datetime
    receiver_cmd = ("wdt -run_as_daemon -overwrite -max_mbytes_per_sec=-1 -progress_report_interval_millis=-1 -directory " + recv_path)
    receiver_process = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, shell=True)
    ## start daemon and return connection url
    connection_url = str(receiver_process.stdout.readline().strip())[1:] 
    ## generate a connection file containing meta data about the daemon 
    meta_data = str("Recvier daemon started by " + getpass.getuser() + " in " + recv_path + " at " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection_file = [meta_data, connection_url]
    export_path = ("/var/app/wdt/pool/" + getpass.getuser() + "_" + str(datetime.datetime.now().strftime("%m_%d-%H:%M_%S")) + ".txt")
    touch(export_path, 'u')
    export_list(export_path, connection_file)
    return export_path

############
## Argument Parser
########
parser = argparse.ArgumentParser(description="A simple wrapper for the WDT CLI Tool. For additional support use 'wdt --help | less'")
parser.add_argument("-s", "--ship", nargs=4, help="Warp a remote directory to another remote directory. Options: src_ssh_alias, src_path, recv_ssh_alias, recv_path")
parser.add_argument("-p", "--push", nargs=3, help="Warp a local directory to a remote directory. Options: src_path, recv_ssh_alias, recv_path")
parser.add_argument("-f", "--fetch", nargs=3, help="Warp a remote directory to a local directory. Options: src_ssh_alias, src_path, recv_path")
### optional arguments 
parser.add_argument("-tr", "--threads", default="8", help="Set the number of threads/ports to participate in this transfer") 
parser.add_argument("-ri", "--report_interval", default="3000", help="Update interval in milliseconds for transfer report updates.")
parser.add_argument("-ts", "--throttle_speed", default="110", help=" Throttle the transfer to an average mbytes per second.")
parser.add_argument("-ow", "--overwrite", default="false", help="Allow the receiver to overwrite existing files in a directory.")
parser.add_argument("-cp", "--custom_parms", nargs='*', default="", help="Inject any additional parameters available in `wdt --help`.") 
### utilities
parser.add_argument("-d", "--daemon", help="Start a receiver daemon on a directory. Returns a connection url to /var/app/wdt.")
parser.add_argument("-m", "--macro", help="Execute a macro by name from /var/app/warp-cli/macros.")
parser.add_argument("-gm", "--gen_macro", help="Generate a new macro. This will overwrite a old macro if named the same.")
parser.add_argument("-in", "--install", help="Attempt an automated install of WDT and dependencies.")
parser.add_argument("-rm", "--uninstall", help="Remove Warp-CLI and config files.")
###
args = parser.parse_args()

############
## Options
########
num_ports = " -num_ports=" + str(args.threads)
avg_mbytes = " -avg_mbytes_per_sec=" + str(args.throttle_speed)
report_interval = " -progress_report_interval_millis=" + str(args.report_interval)
overwrite = " -overwrite=" + str(args.overwrite)
if len(args.custom_parms) > 0:
    options = (num_ports + avg_mbytes + report_interval + overwrite + args.custom_parms)
else: 
    options = (num_ports + avg_mbytes + report_interval + overwrite)

############
## Master Control Flow
########
### Set Vars from Args
if args.gen_macro:
    global macro_name
    macro_name = args.gen_macro

if args.fetch:
    src_ssh = (''.join(str(e) for e in args.fetch[:-2]))
    src_path = (''.join(str(e) for e in args.fetch[1:-1]))
    recv_path = (''.join(str(e) for e in args.fetch[2:]))
    fetch(src_ssh, src_path, recv_path)

if args.push:
    src_path = (''.join(str(e) for e in args.push[:-2]))
    recv_ssh = (''.join(str(e) for e in args.push[1:-1]))
    recv_path = (''.join(str(e) for e in args.push[2:]))
    push(src_path, recv_ssh, recv_path)

if args.ship:
    src_ssh = (''.join(str(e) for e in args.ship[:-3]))
    src_path = (''.join(str(e) for e in args.ship[1:-2]))
    recv_ssh = (''.join(str(e) for e in args.ship[2:-1]))
    recv_path = (''.join(str(e) for e in args.ship[3:]))
    ship(src_ssh, src_path, recv_ssh, recv_path)

### utilities
if args.daemon:
    start_recv_daemon(arg.daemon)
    sys.exit('Exiting on Success!')

if args.gen_macro:
    if len(cmd) == 0:
        sys.exit('No Command to Convert to Macro!')
    else:
        warp(cmd, gen_macro_flg=True, macro_name=args.gen_macro)
        sys.exit("Macro Successfully Generated!")

if args.macro:
    if os.path.exists('/var/app/wdt-cli/macros/' + args.macro):
        sys.exit(args.macro + " is not found in /var/app/wdt-cli/macros/")
    else:
        run_macro(args.macro)
        sys.exit('Transfer Complete!')

if args.install:
    from setup import setup_warp
    setup_warp()
    sys.exit('Install Complete!')

if args.uninstall:
    from setup import uninstall_warp
    uninstall_warp()
    sys.exit('Uninstall Complete!')

###  excute final cmd or return --help
if len(cmd) > 0:
    warp(cmd)
else:
    parser.print_help()
    sys.exit()
