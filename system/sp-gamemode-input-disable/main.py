import os
import evdev
import subprocess
import threading

active_blocks = []
blacklisted_devices = []
active_processes = {}

def get_blacklisted_devices():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    list_path = os.path.join(current_dir, 'conf', 'device_list.txt')
    lines = []
    with open(list_path) as file_in:
        for line in file_in:
            if not line.startswith("#"):
                lines.append(line.rstrip('\n'))
    return lines

def is_gamemode():
    try:
        DESKTOP_SESSION = os.environ.get('DESKTOP_SESSION')
        if DESKTOP_SESSION == "gamescope-wayland":
            return True
        else:
            return False
    except:
        return False

def get_active_devices():
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        return devices
    except:
        return []

def block_device(device):
    global active_blocks
    global active_processes

    if device in active_blocks:
        return
    else:
        print('blocking: ' + device.name + " | ", device.path)
        def run_in_thread(device, dummy):
            block_command = 'evtest --grab {} > /dev/null'.format(device.path)
            proc = subprocess.Popen(block_command, shell=True)
            active_processes[device.path] = proc
            proc.wait()
            stop_blocking_device(device)
            return
        thread = threading.Thread(target=run_in_thread, args=(device, None))
        thread.start()

        print('blocked: ' + device.name + " | ", device.path)
        active_blocks.append(device)

def stop_blocking_device(device):
    global active_blocks
    global active_processes

    print('unblocking: ' + device.name + " | ", device.path)
    if device.path in active_processes:
        active_processes[device.path].kill()
        del active_processes[device.path]

    if device in active_blocks:
        active_blocks.remove(device)
        
    print('unblocked: ' + device.name + " | ", device.path)

def loop():
    global active_blocks
    global blacklisted_devices

    devices = get_active_devices()
    if is_gamemode():
        for device in devices:
            if str(device.name) in blacklisted_devices:
                block_device(device)
    else:
        for blocked_device in active_blocks:
            stop_blocking_device(blocked_device)

def main():
    global blacklisted_devices
    blacklisted_devices = get_blacklisted_devices()

    while True:
        loop()

if __name__ == "__main__":
    main()   