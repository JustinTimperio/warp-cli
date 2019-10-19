#! /usr/bin/python3
#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.5
from global_defuns import * 

############
## Setup WDT
########
def setup_warp(base_dir='/var/app/warp-cli'):
    ## setup dirs
    mkdir('/var/app', 'r')
    mkdir(base_dir, 'r')
    mkdir(base_dir + '/pool', 'r')
    mkdir(base_dir + '/inbound', 'r')
    open_permissions(base_dir)
    ## link warp to warp.py
    os.system('sudo ln -s ' + base_dir + '/core/warp.py /usr/bin/warp') 
    ## build and setup wdt dependencies depending on linux distro
    os_name = os_distro() 
   ############# 
    if 'arch' in os_name.lower():
        aur_tool = input('Do you use a AUR Tool? If so enter the install command for your Tool./nI.E. "pacaur -S": ')
        if len(aur_tool) > 0:
            os.system(aur_tool + " wdt-git")
            sys.exit('Done!')
        else:
            sys.exit('Refer to the manual build guide OR don\'t be stupid a use a AUR manager. :P')
   ############# 
    elif 'fedora 30' or 'fedora 29' or 'fedora 28' in os_name.lower():
        yum('cmake boost-devel openssl jemalloc glog-devel double-conversion-devel make automake gcc gcc-c++ kernel-devel gtest-devel openssl-devel')
   ############# 
    elif 'ubuntu 19' or 'ubuntu 18' or 'debian gnu/linux 9' or 'debian gnu/linux 10' in os_name.lower():
        apt('cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl build-essential libboost-all-dev libssl-dev libgtest-dev')
   ############# 
    #  elif 'opensuse' in os_name.lower():
        #  zypper('-t pattern devel_C_C++')
        #  zypper('cmake jemalloc google-glog boost-base boost-extra double-conversion openssl ')
    else:
        sys.exit('Automated package installs for ' + os_name + ' are not supported.')

    ## download and build wdt from source
    os.system('cd ' + base_dir + ' && git clone https://github.com/facebook/folly.git')
    os.system('cd ' + base_dir + ' && git clone https://github.com/facebook/wdt.git')
    os.system('mkdir ' + base_dir + '/wdt/_build')
    os.system('cd ' + base_dir + '/wdt/_build && cmake ' + base_dir + '/wdt && make -j && sudo make install')

def uninstall_warp(base_dir='/var/app/warp-cli'):
    rm_dir(base_dir, 'r')
    sys.exit('Uninstall Complete!')
