#!/usr/bin/env python3
import re
import os
import pickle
import argparse
import subprocess


def escape_bash_input(astr):
    '''Uses regex subsitution to safely escape bash input.'''
    return re.sub("(!| |\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", astr)


def build_command(typ, arguments, fix_hostname, threads, throttle_speed, report_interval, overwrite, follow_sym, custom_parms):
    '''
    Builds the list of flags and configs neededed for the WDT transfer session
    '''
    options = [
        "-num_ports=" + str(threads),
        "-avg_mbytes_per_sec=" + str(throttle_speed),
        "-progress_report_interval_millis=" + str(report_interval),
        "-overwrite=" + str(overwrite).lower(),
        "-follow_symlinks=" + str(follow_sym).lower()
        ]

    if custom_parms:
        options.append(str(custom_parms))

    # Duplicate Options
    src_options = list(options)
    recv_options = list(options)

    # Apply Hostname Fix If Needed
    if fix_hostname:
        ip_fetch = str("/bin/ip a | /bin/grep -v -E '127.0.0.1|00:00:00:00|inet6' | /bin/grep -Po '\d+.\d+.\d+.\d+\/' | /bin/rev | /bin/cut -c2- | /bin/rev")
        if typ == 'ship':
            ip_cmd = '/usr/bin/ssh ' + arguments[2] + ' ' + ip_fetch

        elif typ == 'push':
            ip_cmd = '/usr/bin/ssh ' + arguments[1] + ' ' + ip_fetch

        elif typ == 'fetch':
            ip_cmd = str(ip_fetch)

        # Capture IP Address
        raw = subprocess.Popen(ip_cmd, stdout=subprocess.PIPE, shell=True)
        hostname = str(raw.stdout.readline().strip())[2:-1]
        src_options.insert(0, str('-hostname ' + hostname))

    # Build the Command Options
    if typ == 'ship':
        cmd = (typ, arguments[0], arguments[1], arguments[2], arguments[3], ' '.join(src_options), ' '.join(recv_options))

    elif typ == 'push':
        cmd = (typ, arguments[0], arguments[1], arguments[2], ' '.join(src_options), ' '.join(recv_options))

    elif typ == 'fetch':
        cmd = (typ, arguments[0], arguments[1], arguments[2], ' '.join(src_options), ' '.join(recv_options))

    return cmd


def run_command(cmd):
    '''
    Run a command build by build_command()
    '''
    if cmd[0] == 'ship':
        # Build and Start Recv Session
        recv_path = escape_bash_input(cmd[4])
        recv_cmd = '/usr/bin/ssh ' + cmd[3] + ' /usr/bin/wdt ' + cmd[5] + ' -directory ' + recv_path
        run_cmd = subprocess.Popen(recv_cmd, stdout=subprocess.PIPE, shell=True)
        wdt_url = str(run_cmd.stdout.readline().strip())[1:]

        # Build and Start Sender Session
        send_path = escape_bash_input(cmd[2])
        send_cmd = '/usr/bin/ssh ' + cmd[1] + ' /usr/bin/wdt ' + cmd[6] + ' -directory ' + send_path + ' -'
        os.system("/bin/echo " + wdt_url + " | " + send_cmd)

    elif cmd[0] == 'push':
        # Build Command
        recv_path = escape_bash_input(cmd[3])
        recv_cmd = '/usr/bin/ssh ' + cmd[2] + ' /usr/bin/wdt ' + cmd[4] + ' -directory ' + recv_path
        send_path = escape_bash_input(cmd[1])
        send_cmd = '/usr/bin/wdt ' + cmd[5] + ' -directory ' + send_path + ' -'

        # Run Command
        os.system(recv_cmd + ' | ' + send_cmd)

    elif cmd[0] == 'fetch':
        # Build Command
        recv_path = escape_bash_input(cmd[3])
        recv_cmd = '/usr/bin/wdt ' + cmd[4] + ' -directory ' + recv_path
        send_path = escape_bash_input(cmd[2])
        send_cmd = '/usr/bin/ssh ' + cmd[1] + ' /usr/bin/wdt ' + cmd[5] + ' -directory ' + send_path + ' -'

        # Run Command
        os.system(recv_cmd + ' | ' + send_cmd)


def store_macro(name, cmd):
    '''
    Stores a macro in /home/user/warp/macros
    '''
    # Store Macro
    macro_name = escape_bash_input(name)
    storage_path = os.path.expanduser('~') + '/.warp/macros'
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    # Pickle Transfer Command
    with open(storage_path + '/' + macro_name, 'wb') as m:
        pickle.dump(cmd, m)
    print('Stored Macro Successfully!')


def run_macro(name):
    '''
    Load a macro pickle and run command.
    '''
    # Read Macro Pickle
    macro_name = escape_bash_input(name)
    storage_path = os.path.expanduser('~') + '/.warp/macros'
    if not os.path.exists(storage_path + '/' + macro_name):
        print('No Macro Found With The Name: ' + name)
        return

    with open(storage_path + '/' + macro_name, 'rb') as m:
        macro = pickle.load(m)
    print('Macro Loaded Successfully!')

    # Run Macro
    run_command(macro)


############
# Argument Parser
########

parser = argparse.ArgumentParser(description="A simple wrapper for the WDT CLI Tool.")

# Core Transfer Commands
parser.add_argument("-s", "--ship", nargs=4, metavar=('SRC_SSH_ALIAS', 'SRC_PATH', 'RECV_SSH_ALIAS', 'RECV_PATH'),
                    help="Warp a remote directory to another remote directory.")
parser.add_argument("-p", "--push", nargs=3, metavar=('SRC_PATH', 'RECV_SSH_ALIAS', 'RECV_PATH'),
                    help="Warp a local directory to a remote directory.")
parser.add_argument("-f", "--fetch", nargs=3, metavar=('SRC_SSH_ALIAS', 'SRC_PATH', 'RECV_PATH'),
                    help="Warp a remote directory to a local directory.")

# Optional Arguments
parser.add_argument("-tr", "--threads", default="8", metavar='INT',
                    help="Set the number of threads/ports for WDT to use.")
parser.add_argument("-ri", "--report_interval", default="3000", metavar='INT',
                    help="Update interval in milliseconds for transfer report updates.")
parser.add_argument("-ts", "--throttle_speed", default="-1", metavar='INT',
                    help=" Throttle the transfer to an average mbytes per second.")
parser.add_argument("-ow", "--overwrite", action='store_true',
                    help="Allow the receiver to overwrite existing files in a directory.")
parser.add_argument("-sym", "--follow_sym", action='store_true',
                    help="Let WDT follow symlinks during transfer.")
parser.add_argument("-cp", "--custom_parms", default="", metavar="-CUSTOM_PARM value",
                    help="Inject any additional parameters available in `wdt --help`.")
parser.add_argument("-fh", "--fix_hostname", action='store_true',
                    help="Fix hostname issues by substituting a machines hostname for local ipv4 address.")

# Utilities
parser.add_argument("-m", "--macro", metavar='MACRO_NAME',
                    help="Execute a macro by name from ~/.warp/macros.")
parser.add_argument("-gm", "--gen_macro", metavar='MACRO_NAME',
                    help="Generate a new macro. This will overwrite any old macro's with the same name.")
parser.add_argument("-v", "--version", action='store_true',
                    help="List Warp-CLI, WDT, and FOLLY Version.")


############
# Trigger Core Args
########

args = parser.parse_args()

if args.version:
    print('Warp-CLI Version: 3.0.2')
    os.system('/usr/bin/wdt --version | tr a-z A-Z')
    os.system('/bin/echo "FOLLY Version:" `cd /opt/warp-cli/build/folly && /usr/bin/git describe`')

if args.ship:
    cmd = build_command('ship', args.ship, args.fix_hostname, args.threads, args.throttle_speed,
                        args.report_interval, args.overwrite, args.follow_sym, args.custom_parms)
    if args.gen_macro:
        store_macro(args.gen_macro, cmd)
    else:
        run_command(cmd)

elif args.push:
    cmd = build_command('push', args.push, args.fix_hostname, args.threads, args.throttle_speed,
                        args.report_interval, args.overwrite, args.follow_sym, args.custom_parms)
    if args.gen_macro:
        store_macro(args.gen_macro, cmd)
    else:
        run_command(cmd)

elif args.fetch:
    cmd = build_command('fetch', args.fetch, args.fix_hostname, args.threads, args.throttle_speed,
                        args.report_interval, args.overwrite, args.follow_sym, args.custom_parms)
    if args.gen_macro:
        store_macro(args.gen_macro, cmd)
    else:
        run_command(cmd)

elif args.macro:
    run_macro(args.macro)
