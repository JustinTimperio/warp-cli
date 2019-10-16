# Warp-CLI _ALPHA-STATE_
A cli wrapper designed to make interacting with Facebook's [Warp Speed Data Transfer (WDT)](https://github.com/facebook/wdt) pain-free.
![Demo_Gif](https://imgur.com/N5uSgNV.gif)

## Abstract
WDT is designed to provide the lowest possible total transfer time when transferring files(to be only hardware and network limited). WDT provides many advantages over most file transfer protocols including: native concurrency, end-to-end encryption, IPV6 support, and the ability to easily achieve +40Gbit speeds when supported. Unlike most file transfer solutions (Except [NORM](https://www.nrl.navy.mil/itd/ncs/products/norm)) WDT provides a native parallel solution for transferring files by separating files into chunks then queueing them across an arbitrary number of threads and TCP connections. In most cases, file transfer times are dramatically reduced compared to traditional methods like FTP or HTTP.

While WDT provides several benefits, it requires a lengthy build process making unsuitable for one time transfers. Additionally, if you are already using a modified version of SSH such as [HPN-SSH](https://www.psc.edu/hpn-ssh), you are likely to see smaller performance gains comparatively. Since WDT is designed to fully saturate even the highest-end hardware, it is likely to overwhelm even the highest-end consumer and enterprise networking hardware. Please consider this when transferring more than a 1TB of files.

### Design
Warp-CLI is mainly a wrapper for the limited existing [CLI app provided by WDT](https://github.com/facebook/wdt/wiki/Getting-Started-with-the-WDT-command-line). While the tool works extremely well, building performant commands for daily use is often unwieldy.

For example: 
`wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/recv | ssh ssh.alias wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/fetch/ -`

Warp-CLI shortens this command to:
 `warp -f ssh.alias /dir/to/fetch/ /dir/to/recv` 

### Macros
Warp-CLI also includes a powerful macro system for repeating custom transfers with a single command. Macros are pre-formed transfer commands (stored in /var/app/warp-cli/macros) that are invoked with `warp -m macro_name`.

To generate a macro:
 `warp -gm daily_backup -f source_ssh /dir/to/backup /dir/to/store/backup -tr 16 -ri 10000 -ow true`

This macro can now be called with:
 `warp -m daily_backup`

### OpenSSH
Warp uses ssh to securely share connection URLs via a standard Linux pipe. It expects the use of an RSA key, which does not require a user password. While it is possible to use PAM authentication or key passwords, I have not yet added this as a feature.
#### URL Sharing While Using  `--ship`
Warp-CLI uses the recommended method for transferring URLs except for the command to send directories between two remote machines. URLs are returned to the host rather than being tunneled through the remote machine to the next remote machine. This allows two remote servers to transfer files between one another without having the permission needed to connect directly via ssh. 
#### SSH Aliases 
Since Warp-CLI is designed mainly for daily use, it is highly recommended(if not assumed) that you already have an ssh alias for the machine you are connecting to. If you don't have an existing SSH alias for the server you are transferring files to, please consider [creating one.](https://www.howtogeek.com/75007/stupid-geek-tricks-use-your-ssh-config-file-to-create-aliases-for-hosts/)

## Usage
Warp-CLI is designed to make WDT usable for daily transfers. It features a number of shortcuts that attempt to make sending files as trivial and intuitive as possible. Additionally, warp.py can be imported into any python3 script, which provides more granular control over transfers. To see a list of all available options use `wdt --help | less`.

Warp-CLI provides three core transfer modes:
- '-s, --ship': Send a remote directory to another remote directory.
    `warp -s source_ssh /dir/to/send dest_ssh /dir/to/recive`  
- '-f, --fetch': Pull a remote directory to a local directory.
    `warp -f source_ssh /dir/to/fetch /dir/to/recive`
- '-p, --push': Send a local directory to a remote directory.
    `warp -p /dir/to/push dest_ssh /dir/to/recive`

### Flags
- '-tr, --threads' default=8: In most cases, 8 threads is sufficient to saturate the connection. You may want to raise or lower this depending on your hardware. 
- '-ri, --report_interval' default=5000: This limits the heartbeat report to 5000 milliseconds(5 seconds).
- '-ts, --throttle_speed' default=105: This setting throttles the transfer to an average mbytes per second.
- '-ow, --overwrite' default=false: Allow the receiver to overwrite existing files.

#### Default Speed Throttle
To provide optimal performance, Warp-CLI throttles transfers to ~90% the capacity of a standard 1 Gigabit NIC by default. This is done because WDT WILL fully saturate a 1 Gigabit NIC to the point that other sessions open on the machine will timeout and crash. You can set this throttle to unlimited by using `--throttle_speed=-1`. 

### Utilities
Warp-CLI provides a number of utilities to streamline the daily use of WTD when sending files in high frequency.

- '-d, --daemon': Start a permanent receiver daemon on a local directory and export a file containing the connection URL and meta-data.
    `warp --daemon /dir/to/recive`
- '-m, --macro': Excute a custom macro from /var/app/warp-cli/config/ by name dir. 
    `warp -m macro_name`
- '-gm, --gen_macro': Enter your transfer command as normal and include the gen_macro with a name for your new macro. 
    `warp -gm macro_name -f source_ssh /dir/to/fetch /dir/to/recive -tr 16 -ri 10000 -ow true`
- '-cp, --custom_parms': Inject any additional parameters available from `wdt --help`. 
    `warp -f /dir/to/recive source_ssh /dir/to/send -c '-skip_writes=true -start_port=12345'`
- '-ir, --install_remote': Attempt to install WDT on a remote machine through ssh.
    `warp -ir ssh_alias`
- '-rm, --uninstall': Uninstall Warp-CLI and config files.
    `warp --uninstall`

## Setup _STILL UNDER DEVELOPMENT_
Since Warp-CLI uses multiple dependencies and configuration files to transfer directories, the script attempts to provide a fully automated installation process for most linux flavors. If your flavor is not supported, please refer to the [manual install documentation,](https://github.com/facebook/wdt/blob/master/build/BUILD.md) Once you install WDT and its dependencies, Warp-CLI will function normally.  

### Automatic Installation
To install WDT and Warp-CLI automaticly on your machine:
1. `sudo mkdir /var/app && sudo chmod 777 /var/app`
2. `cd /var/app && git clone https://github.com/JustinTimperio/warp-cli.git`
3. `python3 /var/app/warp-cli/core/warp.py --install`

### Remote Installation
Since WDT needs to be installed on both machines participating in a transfer, the script attempts to provide an automated install via SSH.  This command will walk you through a set of input prompts if your remote machines os is supported. If not, refer to the manual build guide for the server.
`warp -ir remote_ssh`

### Uninstall
Warp-CLI will remove itself from /var/app/ but WDT will remain installed.
`warp --uninstall`
