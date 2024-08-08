import os
import subprocess

login_screen = r'''
 _  __     _            ____                      
| |/ /   _| |__   ___  |  _ \ ___  ___ ___  _ __  
| ' / | | | '_ \ / _ \ | |_) / _ \/ __/ _ \| '_ \ 
| . \ |_| | |_) |  __/ |  _ <  __/ (_| (_) | | | |
|_|\_\__,_|_.__/ \___| |_| \_\___|\___\___/|_| |_|
by Upwind
'''

# Define a dictionary to store color codes
class colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'

def _check_if_readable(fname):
    """
    Checks if the given filename points to a readable file.

    Args:
        fname (str): The filename to check.

    Returns:
        bool: True if the file is readable, False otherwise.
    """
    try:
        with open(fname, 'r') as f:
            pass
    except:
        return False

    return True

def _run_command(command):
    """
    Runs a system command using subprocess and returns the standard output as a string.

    Args:
        command (str): The command to be executed.

    Returns:
        str: The standard output of the command, or an error message if the command fails.
    """
    try:
        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        # If an exception occurs, return a formatted error message
        return f"Error: {str(e)}"

def check_docker_sock():
    """
    Checks if the Docker socket file exists at the default location (/var/lib/docker.sock).

    Prints messages to indicate the test name, result, and path (if found).
    """
    print(colors.CYAN + '[TEST]', end='')
    print(colors.RESET, end='')
    print(' Check for docker.sock')
    path = '/var/lib/docker.sock'
    if (os.path.exists(path)):
        print(colors.YELLOW + '\t[EXISTS]', end='')
        print(colors.RESET, end='')
        print(' Found in path /var/lib/docker.sock')
    else:
        print(colors.GREEN + '\t[NOT FOUND]', end='')
        print(colors.RESET)

def check_serviceaccount_token():
    """
    Checks for the existence of the service account token file in the default Kubernetes location.

    Prints messages to indicate the test name, result, and path (if found).
    """
    print(colors.CYAN + '[TEST]', end='')
    print(colors.RESET, end='')
    print(' Check for service account token')
    path = '/run/secrets/kubernetes.io/serviceaccount/token'
    if (os.path.exists(path)):
        is_readable = _check_if_readable(path)
        print(colors.YELLOW + '\t[EXISTS]', end='')
        print(colors.RESET, end='')
        print(f' Found in path /run/secrets/kubernetes.io/serviceaccount/token (Readable = {is_readable})')
    else:
        print(colors.GREEN + '\t[NOT FOUND]', end='')
        print(colors.RESET)

KNOWN_ENVS = ['KUBERNETES_SERVICE_PORT', 'KUBERNETES_PORT', 'KUBERNETES_PORT_443_TCP_ADDR', 'KUBERNETES_PORT_443_TCP_PORT',
'KUBERNETES_PORT_443_TCP_PROTO', 'KUBERNETES_SERVICE_PORT_HTTPS', 'KUBERNETES_PORT_443_TCP', 'KUBERNETES_SERVICE_HOST']
def check_kube_related_env():
    """
    Lists environment variables potentially related to Kubernetes and highlights unknown ones.

    Uses the 'env' command and filters output using 'grep' to find lines containing 'kube' (case-insensitive).
    """
    print(colors.CYAN + '[TEST]', end='')
    print(colors.RESET, end='')
    print(' List environment variables related to kubernetes')
    command = 'env | grep -i kube'
    output = _run_command(command).split('\n')
    for line in output:
        var, value = line.split('=')
        if var not in KNOWN_ENVS:
            print('\t' + colors.YELLOW + line, end='')
            print(colors.RESET)
        else:
            print('\t' + line)

def check_kube_related_files():
    """
    Lists files potentially related to Kubernetes using the 'find' command.

    Searches recursively (/) for files containing 'kube' in their name (case-insensitive).
    """
    print(colors.CYAN + '[TEST]', end='')
    print(colors.RESET, end='')
    print(' List files related to kubernetes')
    command = 'find / -iname "*kube*" 2>/dev/null'
    output = _run_command(command).split('\n')
    for line in output:
        print('\t' + line)

KNOWN_MOUNTS = ['/etc/hosts', '/dev/termination-log', '/etc/hostname', '/etc/resolv.conf']
def check_mounts():
    """
    Lists mounts to the node file system and highlights unknown mounts (not in KNOWN_MOUNTS).

    Uses the 'mount' command to list mounts and filters output using 'grep' to find lines starting with '/dev/'.
    """
    print(colors.CYAN + '[TEST]', end='')
    print(colors.RESET, end='')
    print(' List mounts to the node file system')
    command = 'mount | grep "^/dev/"'
    output = _run_command(command).split('\n')
    for line in output:
        known = False
        for known_mount in KNOWN_MOUNTS:
            if known_mount in line:
                known = True

        if not known:
            print('\t' + colors.YELLOW + line, end='')
            print(colors.RESET)
        else:
            print('\t' + line)

def main():
    """
    The main function is the entry point for the script.

    - Prints the login screen.
    - Runs various checks:
        - Docker socket existence
        - Service account token existence
        - Kubernetes-related environment variables
        - Kubernetes-related files
        - Mounted filesystems (highlighting unknown mounts)
    """
    print(colors.PURPLE, end='')
    print(login_screen)

    print()
    check_docker_sock()
    print()
    check_serviceaccount_token()
    print()
    check_kube_related_env()
    print()
    check_kube_related_files()
    print()
    check_mounts()


if __name__ == '__main__':
    main()