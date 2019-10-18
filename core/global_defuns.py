#! /usr/bin/python3
###### Useful Defs for Python3 Projects
#### Version - 1.5

######
## Basic Functions
######
import os, sys, subprocess

def date_to_today(year, month, day, set_name):
    import datetime
    start_date = datetime.date(year, month, day)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    date_delta = abs((start_date - datetime.date.today()).days)
    list_name = {str(end_date - datetime.timedelta(days=x)) for x in range(0, date_delta)}
    return set_name

def yn_frame(prompt, y_defun, n_defun):
    yn = input(prompt + '? (y/n):')
    if yn.lower() in ['y','yes']: 
        y_defun
    elif yn.lower() in ['no','n']:
        n_defun
    else: sys.exit('No usable argument given!') 

def export_list(file_name, list_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'w') as f:
        for i in list_name:
            f.write("%s\n" % i) 

def read_list(file_name):
    list_name = list(open(file_name).read().splitlines()) 
    return list_name

######
### Web Crawling and Downloading Fuctions
######

def dl_url(url, file_name):
    import requests
    r = requests.get(url, allow_redirects=True)
    open(file_name, 'wb').write(r.content)

def is_url_downloadable(url):
    import requests
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

######
### File System Commands and Short-Cuts
######

def open_permissions(path):
    os.system("sudo chmod -R 777 " + path)

def search_fs(path):
    list_name = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn] 
    return list_name

def rm_file(file_path, sudo):
    if sudo == 'r':
        if os.path.exists(file_path):
            os.system('sudo rm ' + file_path)
    if sudo == 'u':
        if os.path.exists(file_path):
            os.system('rm ' + file_path)

def mkdir(dir, sudo):
    if sudo == 'r':
        if not os.path.exists(dir):
            os.system("sudo mkdir " + dir)
    if sudo == 'u':
        if not os.path.exists(dir):
            os.system("mkdir " + dir)

def rm_dir(dir_path, sudo):
    if sudo == 'r':
        if os.path.exists(dir_path):
            os.system('sudo rm -r ' + dir_path)
    if sudo == 'u':
        if not os.path.exists(dir):
            os.system('rm -r ' + dir_path)

######
### Linux System Commands
######
def cpu_core_count():
    core_count = subprocess.check_output("cat /proc/cpuinfo | awk '/^processor/{print $3}' | wc -l", shell=True)
    return str(core_count)[2:-3]

######
### Linux System Package Commands
######
def pacman(package, arg='-S'):
    os.system("sudo pacman " + arg + " " + package + " --needed")

def yum(package, arg='install'):
    os.system("sudo yum " + arg + " " + package)

def apt(package, arg='install'):
    os.system("sudo apt-get " + arg + " " + package)

def zypper(package, arg='install'):
    os.system("sudo zypper " + arg + " " + package)

def pip_install(packages):
    os.system("sudo pip install " + packages)

def aurman_install(packages):
    os.system("aurman -S --needed " + packages)

def os_distro():
    os_name = subprocess.check_output('cat /etc/os-release | grep PRETTY_NAME= | cut -c 13-', shell=True)
    return str(os_name)[2:-3]
