#!/usr/bin/env python
# -*- coding: utf-8 -*-

# tkinter, pyserial
import tkinter as tk
import serial
import subprocess

window = tk.Tk()
window.title("TCM 1601 Controller")
window.config(padx=20, pady=20, height=500, width=500)

ser = serial.Serial()
port = None

# ------- Functions (basic) -------


def send_data_request(s, param_num, addr=1, encoding='utf-8'):
    c = "{:03d}00{:03d}02=?".format(addr, param_num)
    c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
    print(f'Sending: {c}\nEncoded in ({encoding}): {c.encode(encoding)}')
    s.write(c.encode(encoding))
    s.flush()


def send_control_command(s, param_num, data_str, addr=1, encoding='utf-8'):
    c = "{:03d}10{:03d}{:02d}{:s}".format(
        addr, param_num, len(data_str), data_str)
    c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
    print(f'Sending: {c}\nEncoded in ({encoding}): {c.encode(encoding)}')
    return s.write(c.encode(encoding))

# ------- Functions (control) -------


def get_ports():
    global cp_value
    completed = subprocess.run(
        'python3 -m serial.tools.list_ports'.split(), stdout=subprocess.PIPE)
    rtn = completed.stdout.decode().strip().split('\n')[-1]
    cp_value.set(rtn)
    return rtn


def connect_to_tcm1601():
    global port, ser, cs_value
    port = get_ports()
    print(f'Connecting to {port}')
    ser.port = port
    ser.baudrate = 9600
    ser.timeout = 1
    if not ser.is_open:
        ser.open()
    print(f'Connected to {port}')
    cs_value.set('Connected')


def turn_on_turbopump():
    global ser
    send_control_command(ser, 23, '111111')


def turn_off_turbopump():
    global ser
    send_control_command(ser, 23, '000000')


def get_rotation_speed():
    global ser, rs_value
    send_data_request(ser, 309)
    out = ser.read(160).decode()
    print(f'rotation_speed: {out}')
    rotation_speed = out[-6:-3]
    rs_value.set(f'{rotation_speed} Hz')


def get_motor_current():
    global ser, mc_value
    send_data_request(ser, 310)
    out = ser.read(160).decode()
    print(f'motor_current: {out}')
    current = int(out[-6:-3]) / 100
    mc_value.set(f'{current:.2f} A')


# ------- UI -------


# buttons
get_ports_btn = tk.Button(
    window, text='Get Controller Port', command=get_ports)
connect_btn = tk.Button(
    window, text='Connect to Controller', command=connect_to_tcm1601)
turn_on_turbopump_btn = tk.Button(
    window, text='Turn on turbopump', command=turn_on_turbopump)
turn_off_turbopump_btn = tk.Button(
    window, text='Turn off turbopump', command=turn_off_turbopump)
get_rotation_speed_btn = tk.Button(
    window, text='Get rotation speed', command=get_rotation_speed)
get_motor_current_btn = tk.Button(
    window, text='Get motor current', command=get_motor_current)

# labels
controller_port = tk.Label(window, text='Controller port: ')
cp_value = tk.StringVar()
controller_port_value = tk.Label(window, textvariable=cp_value)

connect_status = tk.Label(window, text='Connect status: ')
cs_value = tk.StringVar()
connect_status_value = tk.Label(window, textvariable=cs_value)

rotation_speed = tk.Label(window, text="Rotation speed (Hz): ")
rs_value = tk.StringVar()
rotation_speed_value = tk.Label(window, textvariable=rs_value)

motor_current = tk.Label(window, text="Motor current (A): ")
mc_value = tk.StringVar()
motor_current_value = tk.Label(window, textvariable=mc_value)

# ------- Layout -------

get_ports_btn.grid(row=0, column=0)
controller_port.grid(row=0, column=1)
controller_port_value.grid(row=0, column=2)

connect_btn.grid(row=1, column=0)
connect_status.grid(row=1, column=1)
connect_status_value.grid(row=1, column=2)

turn_on_turbopump_btn.grid(row=2, column=0)
turn_off_turbopump_btn.grid(row=2, column=1)

get_rotation_speed_btn.grid(row=3, column=0)
rotation_speed.grid(row=3, column=1)
rotation_speed_value.grid(row=3, column=2)

get_motor_current_btn.grid(row=4, column=0)
motor_current.grid(row=4, column=1)
motor_current_value.grid(row=4, column=2)


window.mainloop()
