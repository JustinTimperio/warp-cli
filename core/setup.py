#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.3
from global_defuns import * 

############
## Setup WDT
########
def setup_wdt():
    base_dir = ("/var/app/wdt")
    ## setup dirs
    mkdir('/var/app', 'r')
    mkdir(base_dir, 'r')
    mkdir(base_dir + '/pool', 'r')
    mkdir(base_dir + '/inbound', 'r')
    mkdir(base_dir + '/outbound', 'r')
    open_permissions('/var/app')
    ## fetch and update all packages needed for WDT - https://github.com/facebook/wdt/blob/master/build/BUILD.md 
    aurman_install('cmake jemalloc wdt-git')
