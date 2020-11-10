# Warp-CLI - v3.0.2
![Codacy grade](https://img.shields.io/codacy/grade/5215996113c94fc4885dae3aa4a26a35?label=codacy%20grade&style=for-the-badge)
![GitHub](https://img.shields.io/github/license/justintimperio/warp-cli?style=for-the-badge)\
TLDR: Warp is a CLI tool designed to make interacting with Facebook's [Warp Speed Data Transfer (WDT)](https://github.com/facebook/wdt) pain-free.

***Index:***
- [Abstract](https://github.com/JustinTimperio/warp-cli#abstract)
- [CLI Usage](https://github.com/JustinTimperio/warp-cli#cli-usage)
- [Automated Setup](https://github.com/JustinTimperio/warp-cli#setup)
- [Performance Gains](https://github.com/JustinTimperio/warp-cli#performance-gains)


## Abstract
[WDT](https://github.com/facebook/wdt) is designed to provide the highest possible speed when transferring files(to be only hardware and network limited). WDT provides many advantages over most file transfer protocols including: native concurrency, end-to-end encryption, IPV6 support, and the ability to easily achieve +40Gbit speeds when supported. Unlike most file transfer solutions (Except [NORM](https://www.nrl.navy.mil/itd/ncs/products/norm)) WDT provides a native parallel solution for transferring files by separating files into chunks then queuing them across an arbitrary number of threads and TCP connections. In most cases, file transfer times are dramatically reduced compared to traditional methods like FTP or HTTP.

While WDT provides several benefits, it requires a comparatively lengthy build process. Additionally, if you are already using a modified version of SSH such as [HPN-SSH](https://www.psc.edu/hpn-ssh), you are likely to see smaller performance gains. Since WDT is designed to fully saturate even the highest-end enterprise hardware, it will overwhelm your network. Please consider this when transferring more than a 1TB of files.

Warp-CLI is mainly a wrapper for the limited existing [CLI app provided by WDT](https://github.com/facebook/wdt/wiki/Getting-Started-with-the-WDT-command-line). While the tool works extremely well, building performant commands for daily use is often unwieldy.

For example:
```
wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/recv | ssh ssh.alias wdt -num_ports=8 -avg_mbytes_per_sec=100 -progress_report_interval_millis=5000 -overwrite=false -directory /dir/to/fetch/ -
```

Warp-CLI shortens this command to:
```
warp -f ssh_alias /dir/to/fetch/ /dir/to/recv
```

![Demo_Gif](https://imgur.com/N5uSgNV.gif)


## CLI Usage
Warp-CLI features several shortcuts that attempt to make sending files as trivial and intuitive as possible.

### Transfer Modes
Warp-CLI provides three core transfer modes:
- -s, --ship: Send a remote directory to another remote directory.\
    `warp -s source_ssh /dir/to/send dest_ssh /dir/to/receive`  
- -f, --fetch: Pull a remote directory to a local directory.\
    `warp -f source_ssh /dir/to/fetch /dir/to/receive`
- -p, --push: Send a local directory to a remote directory.\
    `warp -p /dir/to/push dest_ssh /dir/to/receive`

### Flags
- `-tr, --threads`: default=8: You may want to raise or lower this depending on your hardware.
- `-ri, --report_interval`: default=5000: This limits the heartbeat report to 5000 milliseconds(5 seconds).
- `-ts, --throttle_speed`: default=-1: This setting throttles the transfer to an average mbytes per second.
- `-ow, --overwrite`: Allow the receiver to overwrite existing files.
- `-sym, --follow_sym`: Let WDT follow symlinks during transfer.
- `-fh, --fix_hostname`: Local transfers often fail unless the WDT receiver session overrides its hostname with its local ipv4 address.
- `-cp, --custom_parms`: Inject any additional parameters available from `wdt --help`.

### Macros
Warp-CLI also includes a macro system for repeating custom transfers with a single command. Macros are stored transfer commands (stored in ~/.warp/macros) that are invoked with `warp -m macro_name`.

To generate a macro:
 ```
 warp -gm daily_backup -f source_ssh /dir/to/backup /dir/to/store/backup -ow -tr 16 -ri 10000 -cp '-skip_writes=true -start_port=12345'
 ```

This macro can now be called with:
 ```
 warp -m daily_backup
```

## Automated Setup
Since WDT requires multiple dependencies, Warp-CLI attempts to provide a fully automated installation process for as many Linux flavors as possible. If your flavor is not supported, please refer to the [manual install documentation](https://github.com/facebook/wdt/blob/master/build/BUILD.md). Once you install WDT and its dependencies Warp-CLI will function normally.  

### Automatic Installation
To install WDT and Warp-CLI automatically on your machine:
``` 
curl https://raw.githubusercontent.com/JustinTimperio/warp-cli/master/build/install.sh | sudo bash
```

**So far, automatic installation is available on:**
- Arch Linux and Manjaro
- Ubuntu 20.xx, 19.xx, 18.xx Workstation and Server
- Debian 10.x and 9.x
- Fedora 32, 31, 30, 29 and 28 Workstation and Server
- CentOS 8

### Uninstall
Warp-CLI will remove itself from the machine but WDT will remain installed.
```
/opt/warp-cli/build/remove.sh
```

### Other Setup and Usage Information

**WDT Incompatible OS's**\
WDT requires CMAKE version > 3.2 or greater, making it incompatible on:
- CentOS 7
- Debian 8

**OpenSSH for URL Sharing**\
Warp uses ssh to securely share connection URLs via a standard Linux pipe. It expects the use of an RSA key, which does not require a user password. While it is possible to use PAM authentication or key passwords, I have not yet added this as a feature.

**SSH Aliases**\
Since Warp-CLI is designed for daily use and it is highly recommended(if not assumed) that you already have an ssh alias for the server you are connecting to. If you don't have an existing SSH alias for the server you are transferring files to, please consider [creating one.](https://www.howtogeek.com/75007/stupid-geek-tricks-use-your-ssh-config-file-to-create-aliases-for-hosts/)

## Performance Gains
Below are timed downloads(in seconds) over my personal network which is 1 Gigabit. Each progressive transfer increases the total size of the transfer in GB, while reducing the total number of files being transferred. WDT easily maintains near full 1 Gigabit saturation across all 3 transfers while HPN-SFTP and SSH struggle to transfer multiple small files(single-thread limited). With encryption disabled HPN-SSH reaches full saturation when transferring large files, while stock SSH continues to struggle under heavy load. If you have access to +10 Gigabit networking hardware you can expect WDT to scale to ~40 Gigabit and HPN-SSH to scale to ~10 Gigabit.

![Performance Graph](https://i.imgur.com/ax7eKzj.png)
