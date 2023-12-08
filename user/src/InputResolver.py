import os,sys

import evdev
import subprocess
import threading

active_blocks = []
blacklisted_devices = []
active_processes = {}
user_password = "password"

class InputDevice:
    def __init__(self, name, path) -> None:
        self.name = name
        self.path = path

class InputResolver:

    def get_user_password():
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            list_path = os.path.join(current_dir, 'conf', 'password.txt')
            with open(list_path) as file_in:
                for line in file_in:
                    return line
        except Exception as e:
            print("Missing './src/conf/password.txt' file!!")
            raise e
    
    def get_blacklisted_devices():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        list_path = os.path.join(current_dir, 'conf', 'device_list.txt')
        lines = []
        with open(list_path) as file_in:
            for line in file_in:
                if not line.startswith("#"):
                    lines.append(line.rstrip('\n'))
        return lines

    def get_active_devices():
        try:
            devices = []
            for path in evdev.list_devices():
                device = evdev.InputDevice(path)
                devices.append(InputDevice(device.name, device.path))
                device.close()
            return devices
        except:
            print("Failed to get Active devices!")
            return []

    def block_device(device: InputDevice):
        global active_blocks
        global active_processes
        global user_password

        if device.path in active_blocks:
            return
        else:
            print('blocking: ' + device.name + " | ", device.path)
            def run_in_thread(device, dummy):
                block_command = 'sudo -S <<< {0} -k /usr/bin/evtest --grab {1} > /dev/null'.format(user_password, device.path)
                proc = subprocess.Popen(block_command, shell=True)
                active_processes[device.path] = proc
                proc.wait()
                InputResolver.stop_blocking_device(device)
                return
            thread = threading.Thread(target=run_in_thread, args=(device, None))
            thread.start()

            print('blocked: ' + device.name + " | ", device.path)
            active_blocks.append(device.path)

    def stop_blocking_device(device: InputDevice):
        global active_blocks
        global active_processes

        print('unblocking: ' + device.name + " | ", device.path)
        if device.path in active_processes:
            active_processes[device.path].kill()
            del active_processes[device.path]

        if device in active_blocks:
            active_blocks.remove(device)
            
        print('unblocked: ' + device.name + " | ", device.path)

    def init():
        global blacklisted_devices
        global user_password

        blacklisted_devices = InputResolver.get_blacklisted_devices()
        user_password = InputResolver.get_user_password()

    def close_devices():
        pass

    def loop(state):
        try:
            global active_blocks
            global blacklisted_devices

            devices = InputResolver.get_active_devices()
            if state:
                for device in devices:
                    if str(device.name) in blacklisted_devices:
                        InputResolver.block_device(device)
            else:
                for blocked_device in active_blocks:
                    InputResolver.stop_blocking_device(blocked_device)
        except Exception as e:
            print(e)