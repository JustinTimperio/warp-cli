#! /usr/bin/python3
#### WDT Wrapper for Uni-Cast - https://github.com/facebook/wdt
## Version 1.5
from global_defuns import * 

############
## Setup WDT
########
if search('arch', os_name.lower()):
    aur_tool = input('Do you use a AUR Tool? If so enter the install command for your Tool./nI.E. "pacaur -S": ')
    if len(aur_tool) > 0:
        os.system(aur_tool + " wdt-git")
        sys.exit('Done!')
    else:
        sys.exit('Refer to the manual build guide OR don\'t be stupid a use a AUR manager. :P')
   ############# 
elif search('ubuntu 19 | ubuntu 18 | debian gnu/linux 9 | debian gnu/linux 10', os_name.lower()):
    apt('cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl build-essential libboost-all-dev libssl-dev libgtest-dev')
   ############# 
elif search('fedora 30 | fedora 29 | fedora 28', os_name.lower()):
    yum('cmake boost-devel openssl jemalloc glog-devel double-conversion-devel make automake gcc gcc-c++ kernel-devel gtest-devel openssl-devel')
############# 
#  elif 'opensuse' in os_name.lower():
    #  zypper('-t pattern devel_C_C++')
    #  zypper('cmake jemalloc google-glog boost-base boost-extra double-conversion openssl ')
else:
    sys.exit('Automated package installs for ' + os_name + ' are not supported.')

