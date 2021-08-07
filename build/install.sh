#!/usr/bin/env bash

# Base Vars
osname=$(cat /etc/*release | grep -Pi '^ID=' | head -1 | cut -c4- | sed -e 's/^"//' -e 's/"$//')
base=/opt/warp-cli
bd=$base/build
bd_tmp=$bd/wdt/_build
cmakelist=$bd/wdt/CMakeLists.txt

#########################################
# Install Dependencies for Each Distro
#######################################

echo '===================================='
echo '      Installing Dependencies'
echo '===================================='
echo ''

## DEBIAN
if [[ $osname == 'ubuntu' ]] || [[ $osname == 'debian' ]]; then
  # Install Dependencies
  apt --yes install git python3 cmake libjemalloc-dev libgoogle-glog-dev libboost-system-dev libdouble-conversion-dev openssl build-essential libboost-all-dev libssl-dev libgtest-dev libevent-dev

## CENTOS
elif [[ $osname == 'centos' ]] || [[ $osname == 'fedora' ]]; then
  # Install Dependencies
  yum -y install git python38 cmake boost-devel openssl jemalloc glog-devel double-conversion-devel make automake gcc gcc-c++ kernel-devel gtest-devel openssl-devel libevent-devel

## ARCH
elif [[ $osname == 'arch' ]] || [[ $osname == 'manjaro' ]]; then
  # Install Dependencies
  pacman -S --noconfirm --needed git python glibc bash double-conversion gflags google-glog openssl git cmake boost jemalloc gtest

## NOT SUPPORTED
else
  echo $osname Is Not Supported!
  exit 1
fi

#####################
# Install Warp-CLI
###################

echo ''
echo '===================================='
echo '        Installing Warp-CLI'
echo '===================================='
echo ''

if ! test -f $base; then
  rm -R $base
fi

git clone https://github.com/JustinTimperio/warp-cli.git $base

# Link to /usr/bin
ln -sf $base/core/warp.py /usr/bin/warp

#################################
# Manual Build of WDT and Libs
###############################

echo ''
echo '===================================='
echo '          Fetching Folly'
echo '===================================='
echo ''

# Fetch Folly
git clone https://github.com/facebook/folly.git $bd/folly
cd $bd/folly
git checkout ca78b4cec2f4c94189d487120d6beae6a86ada65
cd $bd 

echo ''
echo '===================================='
echo '           Fetching WDT'
echo '===================================='
echo ''

# Clone and Build WDT From Source
git clone https://github.com/facebook/wdt.git $bd/wdt
cd $bd/wdt
git checkout 0184e65ecd50ab337971ac7ddcb2d83f209e0ef0
cd $bd 
mkdir $bd_tmp

# Patch CMakeList.txt If Needed
if ! grep -q '"${FOLLY_SOURCE_DIR}/folly/lang/CString.cpp"' $cmakelist; then
  sed -i '/^"${FOLLY_SOURCE_DIR}\/folly\/ScopeGuard.cpp"/a "${FOLLY_SOURCE_DIR}\/folly\/lang\/CString.cpp"' $cmakelist
else
  echo Patching CMakeList.txt Was Unnecessary!
fi

echo ''
echo '===================================='
echo '          Installing WDT'
echo '===================================='
echo ''

# Make and Install
cd $bd_tmp
cmake -DCMAKE_INSTALL_PREFIX="/usr" -DCMAKE_BUILD_TYPE=Release ../
make -j
make install

echo ''
echo '===================================='
echo ''
warp -v 
