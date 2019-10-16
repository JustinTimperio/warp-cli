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
    open_permissions('/var/app/warp-cli')
    
    ## build and setup wdt dependencies depending on linux distro
    os_name = os_distro() 
   ############# 
    if 'arch' in os_name.lower():
        pacman('cmake jemalloc google-glog boost double-conversion openssl')
        
        aurman('wdt-git')
   ############# 
    elif 'ubuntu' in os_name.lower():
        apt('cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl')
   ############# 
    elif 'fedora' or 'redhat' or 'centos' in os_name.lower():
        yum('cmake jemalloc glog boost double-conversion openssl')
   ############# 
    #  else:
    #      sys.exit('Automated package installs for ' + os_name + ' are not supported.')

    ## download and build wdt for source
    os.system('cd ' + base_dir + ' && sudo git clone https://github.com/facebook/wdt.git')
    os.system('sudo cmake ' + base_dir + '')

#  def gen_ssh_alias():
    #  input
