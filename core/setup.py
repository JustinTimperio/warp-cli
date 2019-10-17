#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.3
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
        pacman('cmake jemalloc google-glog boost double-conversion openssl')
       
        aur_tool = input('Do you use a AUR Tool? If so enter the install command for your Tool./nI.E. "pacaur -S": ')
        if len(aur_tool) > 0:
            os.system(aur_tool + " wdt-git")
        else:
            sys.exit('Refer to manual build guide. Building without an AUR manager is NOT supported.')
   ############# 
    elif 'ubuntu' in os_name.lower():
        apt('cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl build-essential libboost-all-dev libssl-dev')
   ############# 
    elif 'fedora' or 'redhat' in os_name.lower():
        yum('cmake jemalloc glog boost double-conversion openssl')
   ############# 
    else:
        sys.exit('Automated package installs for ' + os_name + ' are not supported.')

    ## download and build wdt from source
    os.system('cd ' + base_dir + ' && git clone https://github.com/facebook/folly.git')
    os.system('cd ' + base_dir + ' && git clone https://github.com/facebook/wdt.git')
    #  os.system('sudo cmake ' + base_dir)

