#!/usr/bin/env bash

if [[ "root" == `whoami` ]]; then
   "
                                    Hi

It is not advised to run this whole install script as root.  You will be prompted for the sudo p/w when it is needed. Please re-run w/out using sudo or as root.  

If you do still wish to run as root, simply delete this if statement and re-run...brew is going to complain though.

"
   exit 33;
fi


# Base Vars
base=/opt/warp-cli
bd=$base/build
bd_tmp=$bd/wdt/_build

#########################################
# Tested on OSX Catalina 10.15.7
#######################################

echo '===================================='
echo '      Installing Dependencies'
echo '===================================='
echo ''

# Check if developertools are installed.
echo """
Checking to see if the OSX developer tools are installed. 
If not, you'll get a popup asking if you'd like to install
the tools. You do. Install them, this will take ~15m.  If
You have the tools installed, you'll just see your version
of git. oh- if you do install the dev tools, you won't 
need to do it again unless you decide to upgrade.

A few commands will require you to enter your sudo p/w, ie:
the final install.

"""

sleep 4

echo "Ok, checking if git is installed...."

git --version

echo "Well, off we go."

sleep .5

echo ''
echo '===================================='
echo '      BREW STUFF                    '
echo '===================================='
echo ''

brew install cmake
brew install glog gflags boost
brew install double-conversion
brew install openssl
brew install folly


#####################
# Install Warp-CLI
#####################

echo ''
echo '===================================='
echo '        Installing Warp-CLI'
echo '===================================='
echo ''

if ! test -f $base; then
  sudo rm -rf $base
fi

sudo git clone https://github.com/iamh2o/warp-cli.git $base ## <-=- Change back after testing

# Link to /usr/bin
sudo rm /usr/local/bin/warp
sudo ln -s $base/core/warp.py /usr/local/bin/warp

#################################
# Manual Build of WDT and Libs
###############################

echo ''
echo '===================================='
echo '           Fetching WDT'
echo '===================================='
echo ''

# Clone and Build WDT From Source
sudo git clone https://github.com/facebook/wdt.git $bd/wdt
sudo cd $bd 
sudo mkdir $bd_tmp

echo ''
echo ' Hack To Get Around Version Incompatability Bug    '
echo ' This should work, but has some risk to corrupting '
echo ' the source code being manipulated.                '
echo ''

# The integer set for the WDT_VERSION_BUIILD IS
# Too large for MAC compilers for some reason
# And throw a ld: malformed 64-bit a.b.c.d.e version number: 1.32.1910230
# error. I'm arbitrarily setting it to luck 64, hopefully this is
# resolved in the main branch soon

PVER=`grep -sE 'WDT_VERSION_BUILD' $bd/wdt/WdtConfig.h | cut -d " " -f 3`
echo ' DETECTED WDT_V_B: $PVER '
CMD1="perl -pi -e 's/$PVER/64/g;' $bd/wdt/CMakeLists.txt"
echo $CMD1
sudo chmod a+wrx $bd/wdt/
sudo chmod a+wrx $bd/wdt/*
eval $CMD1
CMD2="perl -pi -e 's/$PVER/64/g;' $bd/wdt/WdtConfig.h"
echo $CMD2
eval $CMD2


echo ''
echo '===================================='
echo '          Installing WDT            '
echo '===================================='
echo ''

# Make and Install wdt
sudo cd $bd_tmp
sudo cmake $bd/wdt -G "Unix Makefiles" -DBUILD_TESTING=off -DOPENSSL_ROOT_DIR=/usr/local/opt/openssl -DWDT_USE_SYSTEM_FOLLY=/usr/local/Cellar/folly/*/
sudo make -j 2

sudo make install

#echo ''
#echo '===============and=================='
#echo ''
warp -v 
