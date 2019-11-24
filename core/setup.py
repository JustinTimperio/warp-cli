#! /usr/bin/env python3
#### WDT Wrapper - https://github.com/facebook/wdt
## Version 2.1.2
from python_scripts import *

############
## Setup WDT
########
def build_wdt(base_dir):
    import re
    ## build and setup wdt dependencies depending on linux distro
    os_name = os_distro()
    #############
    if re.search(r'arch', os_name.lower()):
        aur_tool = input('Enter the install command for your tool... (I.E. "pacaur -S"): ')
        if len(aur_tool) > 2:
            os.system(aur_tool + " wdt-git")
            sys.exit('Done!')
        else:
            sys.exit('Refer to the manual build guide OR don\'t be stupid and use a AUR manager. :P')
    #############
    elif re.search(r'(fedora 30|fedora 29|fedora 28)', os_name.lower()):
        yum('cmake boost-devel openssl jemalloc glog-devel double-conversion-devel make automake gcc gcc-c++ kernel-devel gtest-devel openssl-devel libevent-devel')
    #############
    elif re.search(r'(ubuntu 19|ubuntu 18|debian gnu/linux 9|debian gnu/linux 10)', os_name.lower()):
        apt('cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl build-essential libboost-all-dev libssl-dev libgtest-dev libevent-dev')
    #############
    else:
        sys.exit('Automated package installs for ' + os_name + ' are not supported.')
    
    ## download and build wdt from github source
    mkdir(base_dir + '/build', 'u')
    os.system('cd ' + base_dir + '/build && git clone https://github.com/facebook/folly.git')
    os.system('cd ' + base_dir + '/build/folly && git checkout v2019.09.02.00')
    ## unused command while folly is broke
    #  os.system('cd ' + base_dir + '/build/folly && git checkout "$(git describe --abbrev=0 --always)"')
    os.system('cd ' + base_dir + '/build && git clone https://github.com/facebook/wdt.git')
    mkdir(base_dir + '/build/wdt/_build', 'u')
    os.system('cd ' + base_dir + '/build/wdt/_build && cmake -DCMAKE_INSTALL_PREFIX="/usr" -DCMAKE_BUILD_TYPE=Release ../ && make -j && sudo make install')

############
## Setup Warp-CLI
########
def setup_warp(base_dir):
    ## setup warp-cli dirs
    mkdir(base_dir + '/pool', 'u')
    mkdir(base_dir + '/macros', 'u')
    os.system('sudo chmod 777 ' + base_dir + '/pool ' + base_dir + '/macros')
    ## link warp in bash to warp.py
    rm_file('/usr/bin/warp', 'r')
    os.system('sudo ln -s ' + base_dir + '/core/warp.py /usr/bin/warp')
    print('Warp-CLI is now setup and registered in /usr/bin!')
    
    ### Start Automated Setup
    build = yn_frame('Do you want to attempt an automatic WDT build and install?')
    if build == True:
        build_wdt(base_dir, dev)
        os.system("echo '=============================' && warp --version && echo '============================='")
    if build == False:
        print('Refer to https://github.com/facebook/wdt/blob/master/build/BUILD.md for manual builds.')

def setup_warp_remote(ssh_alias, base_dir, dev=False):
    ## tunnel to a remote machine and install warp-cli
    git_clone = ' "cd ' + base_dir + ' && git clone --recurse-submodules https://github.com/JustinTimperio/warp-cli.git &&'
    build = ' python3 ' + base_dir + '/warp-cli/core/warp.py --install"' 
    if dev == False:
        os.system('ssh ' + ssh_alias + git_clone + build)
    if dev == True:
        os.system('ssh ' + ssh_alias + git_clone + ' cd warp-cli/ && git checkout development && git submodule update --init --recursive &&' + build)

def uninstall_warp(base_dir):
    rm_dir(base_dir, 'r')
    rm_file('/usr/bin/warp', 'r')
    print('Warp-CLI Uninstalled!')
