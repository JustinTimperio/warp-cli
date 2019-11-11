# Warp-CLI - _Alpha v2.0_
TLDR: Warp is a CLI tool designed to make interacting with Facebook's [Warp Speed Data Transfer (WDT)](https://github.com/facebook/wdt) pain-free.

## Abstract
[WDT](https://github.com/facebook/wdt) is designed to provide the highest possible speed when transferring files(to be only hardware and network limited). WDT provides many advantages over most file transfer protocols including: native concurrency, end-to-end encryption, IPV6 support, and the ability to easily achieve +40Gbit speeds when supported. Unlike most file transfer solutions (Except [NORM](https://www.nrl.navy.mil/itd/ncs/products/norm)) WDT provides a native parallel solution for transferring files by separating files into chunks then queuing them across an arbitrary number of threads and TCP connections. In most cases, file transfer times are dramatically reduced compared to traditional methods like FTP or HTTP.

While WDT provides several benefits, it requires comparatively lengthy build process. Additionally, if you are already using a modified version of SSH such as [HPN-SSH](https://www.psc.edu/hpn-ssh), you are likely to see smaller performance gains. Since WDT is designed to fully saturate even the highest-end enterprise hardware, it is likely to overwhelm your network. Please consider this when transferring more than a 1TB of files.

## Performance Gains
Below are timed downloads(in seconds) over my personal network which is 1 Gigabit. Each progressive transfer increases the total size of the transfer in GB, while reducing the total number of files being transferred. WDT easily maintains near full 1 Gigabit saturation across all 3 transfers while HPN-SFTP and SSH struggle to transfer multiple small files(single-thread limited). With encryption disabled HPN-SSH reaches full saturation when transferring large files, while stock SSH continues to struggle under heavy load. If you have access to +10 Gigabit networking hardware you can expect WDT to scale to ~40 Gigabit and HPN-SSH to scale to ~10 Gigabit.

![Performance Graph](https://i.imgur.com/ax7eKzj.png)

## Design
Warp-CLI is mainly a wrapper for the limited existing [CLI app provided by WDT](https://github.com/facebook/wdt/wiki/Getting-Started-with-the-WDT-command-line). While the tool works extremely well, building performant commands for daily use is often unwieldy.

For example:\
`wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/recv | ssh ssh.alias wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/fetch/ -`

Warp-CLI shortens this command to:\
 `warp -f ssh.alias /dir/to/fetch/ /dir/to/recv`

![Demo_Gif](https://imgur.com/N5uSgNV.gif)

Warp.py can also be imported into any python3 script and then used independently of the CLI to send and receive directories.

## Usage
Warp-CLI features a number of shortcuts that attempt to make sending files as trivial and intuitive as possible.

### Transfer Modes
Warp-CLI provides three core transfer modes:
- -s, --ship: Send a remote directory to another remote directory.\
    `warp -s source_ssh /dir/to/send dest_ssh /dir/to/receive`  
- -f, --fetch: Pull a remote directory to a local directory.\
    `warp -f source_ssh /dir/to/fetch /dir/to/receive`
- -p, --push: Send a local directory to a remote directory.\
    `warp -p /dir/to/push dest_ssh /dir/to/receive`

### Flags
- `-tr, --threads` - default=8: In most cases, 8 threads is sufficient to saturate the connection. You may want to raise or lower this depending on your hardware.
- `-ri, --report_interval`- default=5000: This limits the heartbeat report to 5000 milliseconds(5 seconds).
- `-ts, --throttle_speed` - default=-1: This setting throttles the transfer to an average mbytes per second.
- `-ow, --overwrite` - default=false: Allow the receiver to overwrite existing files.

### Macros
Warp-CLI also includes a macro system for repeating custom transfers with a single command. Macros are stored transfer commands (stored in ~/warp-cli/macros) that are invoked with `warp -m macro_name`.

To generate a macro:\
 `warp -gm daily_backup -f source_ssh /dir/to/backup /dir/to/store/backup -tr 16 -ri 10000 -ow true -cp '-skip_writes=true -start_port=12345'`

This macro can now be called with:\
 `warp -m daily_backup`

### Utilities
Warp-CLI provides a number of utilities to streamline the daily use of WTD when sending files in high frequency.

- -cp, --custom_parms: Inject any additional parameters available from `wdt --help`.\
    `warp -f /dir/to/receive source_ssh /dir/to/send -cp '-skip_writes=true -start_port=12345'`
- -m, --macro: Execute a custom macro from /var/app/warp-cli/config/ by name.\
    `warp -m macro_name`
- -gm, --gen_macro: Enter your transfer command as normal and include the gen_macro with a name for your new macro.\
    `warp -gm macro_name -f source_ssh /dir/to/fetch /dir/to/receive -tr 16 -ri 10000 -ow true`
- -d, --daemon: Start a permanent receiver daemon on a local directory and export a file containing the connection URL and meta-data.\
    `warp --daemon /dir/to/receive`
- -i, --install: Attempt to install WDT and dependencies.\
    `warp --install`
- -ri, --remote_install: Attempt to install WDT and dependencies on a remote machine.\
    `warp -ri ssh.alias /dir/to/install`
- -rm, --uninstall: Uninstall Warp-CLI and config files.\
    `warp --uninstall`

## Setup - _STILL UNDER DEVELOPMENT_
Since WDT requires multiple dependencies, Warp-CLI attempts to provide a fully automated installation process for as many linux flavors as possible. If your flavor is not supported, please refer to the [manual install documentation](https://github.com/facebook/wdt/blob/master/build/BUILD.md). Once you install WDT and its dependencies Warp-CLI will function normally.  

### Automatic Installation
To install WDT and Warp-CLI automatically on your machine:
1. `git clone https://github.com/JustinTimperio/warp-cli.git`
2. `cd warp-cli/ && git submodule update --init --recursive`
3. `python3 core/warp.py --install`

So far, automatic installation is available on:
- Arch Linux
- Ubuntu 19.xx and 18.xx Workstation and Server
- Debian 10.x and 9.x
- Fedora 30, 29 and 28 Workstation and Server

WDT requires CMAKE version > 3.2 or greater, making it incompatible on:
- CentOS 7
- Debian 8

### Uninstall
Warp-CLI will remove itself from the machine but WDT will remain installed.\
`warp --uninstall`


### OpenSSH for URL Sharing
Warp uses ssh to securely share connection URLs via a standard Linux pipe. It expects the use of an RSA key, which does not require a user password. While it is possible to use PAM authentication or key passwords, I have not yet added this as a feature.
#### URL Sharing Security While Using  `--ship`
Warp-CLI uses the recommended method for transferring URLs except for the command to send directories between two remote machines. URLs are returned to the host rather than being tunneled through the remote machine to the next remote machine. This allows two remote servers to transfer files between one another without having the permission needed to connect directly via ssh.
#### SSH Aliases
Since Warp-CLI is designed mainly for daily use, it is highly recommended(if not assumed) that you already have an ssh alias for the server you are connecting to. If you don't have an existing SSH alias for the server you are transferring files to, please consider [creating one.](https://www.howtogeek.com/75007/stupid-geek-tricks-use-your-ssh-config-file-to-create-aliases-for-hosts/)
