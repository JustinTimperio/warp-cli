# Warp-CLI _DEV-STATE_
A trivial python cli wrapper designed to make interacting with Facebook's Open Source Library "Warp Speed Data Transfer" fast and painfree.

## Usage
The Warp CLI supports 4 main transfer modes:
    '--ship': Send a remote directory to another remote directory.
    '--pull': Pull a remote directory to a local directory.
    '--push': Send a local directory to a remote directory.
    '--daemon': Start a reciver daemon on a local directory and export a file containing the connection URL and meta-data.

### Usage Example
To send a directory between servers from a remote device:  
`warp --ship source_ssh_alias /dir/to/send dest_ssh_alias /dir/to/recive`  
To fetch a remote directory:  
`warp --pull /dir/to/recive source_ssh_alias /dir/to/send`  
To send a local directory:  
`warp --push /dir/to/send dest_ssh_alias /dir/to/recive`  
To start a daemon on a directory:  
`warp --daemon /dir/to/recive`  

## Setup
Since Warp uses multiple dependencies and configuration files to transfer directories, a detailed set of setup utilities are provided.
It is also worth nothing that the build process for WDT is quite lengthy making it unsutiable for onetime transfers less than 500GB in size.

### Installation
To install the WDT and Warp-CLI:
1. `sudo mkdir /var/app && sudo chmod 777 /var/app`
2. `cd /var/app && git clone https://github.com/JustinTimperio/warp-cli.git`
3. `python3 /var/app/warp-cli/core/warp.py --setup`

### SSH Alias Creation
Warp uses ssh to securely share connection urls via a standard linux pipe. It expects the use of an RSA key, which don't require a user password. While it is possible to allow for the use of PAM authentication or key passwords, I have yet to add this as a feature.
If you don't have an existing SSH alias for a server, you can generate one using `warp --create_alias`.

