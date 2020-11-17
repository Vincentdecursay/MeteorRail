#!/usr/bin/env python3
import RPi.GPIO as io
import sys, tty, termios, time
from subprocess import call
import configparser


io.setmode(io.BCM)

config = configparser.ConfigParser()
config.read('config.txt')

# STEPPER MOTOR CONFIG
# GPIO pins used for the stepper motor
motor_enable_pin = int(config['STEPPER_MOTOR']['motor_enable_pin'])
motor_direction_pin = int(config['STEPPER_MOTOR']['motor_direction_pin'])
motor_step_pin = int(config['STEPPER_MOTOR']['motor_step_pin'])

motor_delay = float(config['STEPPER_MOTOR']['motor_delay'])             # By playing with this delay you can influence the rotational speed.
pulses_per_rev = int(config['STEPPER_MOTOR']['pulses_per_rev'])         # This can be configured on the driver using the DIP-switches

# CAMERA CONFIG
camera_trigger_pin = int(config['CAMERA']['camera_trigger_pin'])    # GPIO pin used to trigger the camera

camera_trigger_delay = float(config['CAMERA']['camera_trigger_delay'])          # The duration for the camera to detect it had been trigerred, reduce it if the camera take more picture than it should
camera_vibration_delay = float(config['CAMERA']['camera_vibration_delay'])      # The duration to wait for the all setup to stabilize to reduce moving blur
camera_taking_picture_delay = float(config['CAMERA']['camera_taking_picture_delay']) #Waiting for the camera to take a picture

# STACKING CONFIG
number_of_shot = int(config['STACKING']['number_of_shot'])
number_of_step = int(config['STACKING']['number_of_step'])


# GPIO CONFIGURATION
io.setup(motor_enable_pin, io.OUT)
io.setup(motor_direction_pin, io.OUT)
io.setup(motor_step_pin, io.OUT)
io.setup(camera_trigger_pin, io.OUT)

# GPIO INITIALIZATION
io.output(motor_enable_pin, False)
io.output(motor_step_pin, False)
io.output(motor_direction_pin, True)
io.output(camera_trigger_pin, False)




## STEPPER MOTOR FUNCTION
# enable the motor, the motor will stop any unwanted rotation
def stepper_enable():
    io.output(motor_enable_pin, False)

# disable the motor, the motor will move freely
def stepper_disable():
    io.output(motor_enable_pin, True)

def step_once():
    io.output(motor_step_pin, True)
    time.sleep(motor_delay)
    io.output(motor_step_pin, False)
    time.sleep(motor_delay)

def step_forward():
    io.output(motor_direction_pin, True)
    time.sleep(motor_delay)
    step_once()

def step_reverse():
    io.output(motor_direction_pin, False)
    time.sleep(motor_delay)
    step_once()

# Full rotation forward, you need to configure the number of step in a 360 degree rotation
def rotate_forward():
    for x in range(0, pulses_per_rev):
            step_forward()
# Full rotation backward
def rotate_reverse():
    for x in range(0, pulses_per_rev):
            step_reverse()

# CAMERA FUNCTION
def take_picture():
    io.output(camera_trigger_pin, True)
    time.sleep(camera_trigger_delay)
    io.output(camera_trigger_pin, False)

def stacking():
    for x in range(0, number_of_shot):
            time.sleep(camera_vibration_delay)
            take_picture()
            time.sleep(camera_taking_picture_delay)
            print_current_task('stacking : picture ' + str(x + 1) + '/' + str(number_of_shot), 0 )
            for y in range(0, number_of_step):
                step_forward()



# BLESSED INTERFACE
# https://github.com/jquast/blessed
from blessed import Terminal

term = Terminal()

def print_screen():
        print(term.orangered("      /\/\   ___| |_ ___  ___  _ __  / _| |_ __ _  ___| | __ ") +  term.orange(" / _ \ / |"))
        print(term.orangered("     /    \ / _ | __/ _ \/ _ \| '__| \ \| __/ _` |/ __| |/ / ") +  term.orange("| ' ' || |"))
        print(term.orangered("    / /\/\ |  __| ||  __| (_) | |    _\ | || (_| | (__|   <  ") +  term.orange("| |_| _| |"))
        print(term.orangered("    \/    \/\___|\__\___|\___/|_|    \__/\__\__,_|\___|_|\_\ ") +  term.orange(" \___(_|_|"))
        print('<=========================================================================>')
        print(term.orangered("current task:"))
        print("")
        print("")
        print("")
        print("")
        print('<=========================================================================>')
        print(term.orangered('q') + ' quit | ' + term.orangered('e') + ' enable motor | ' + term.orangered('d') + ' disable motor ')
        print(term.orangered('r') + ' reverse step | ' + term.orangered('f') + ' forward step | ' + term.orangered('t') + ' reverse rotation | ' + term.orangered('g') + ' forward rotation')
        print(term.orangered('s') + ' take a shot | ' + term.orangered('z') + ' begin stacking!')
        
def print_current_task(current_task, status):
        if status == 0 :
                print(term.move_y(6) + term.clear_eol() + term.orange(current_task))
        else:
                print(term.move_y(6) + term.clear_eol() + term.green(current_task))

# The getch method can determine which key has been pressed
# by the user on the keyboard by accessing the system files
# It will then return the pressed key as a variable
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


with term.fullscreen(),term.cbreak():
        
        val = ''
        print_screen()
        
        while val.lower() != 'q':
                val = getch()
                if val.lower() == 'r':
                        step_forward()
                        print_current_task("reverse step",1)
                elif val.lower() == 'f':
                        step_reverse()
                        print_current_task("forward step",1)
                elif val.lower() == 't':
                        print_current_task("reverse rotation",0)
                        rotate_reverse()
                        print_current_task("reverse rotation",1)
                elif val.lower() == 'g':
                        print_current_task("forward rotation",0)
                        rotate_forward()
                        print_current_task("forward rotation",1)
                elif val.lower() == 'e':
                        stepper_enable()
                        print_current_task("motor enabled",1)
                elif val.lower() == 'd':
                        stepper_disable()
                        print_current_task("motor disabled",1)
                elif val.lower() == 's':
                        take_picture()
                        print_current_task("took a shot",1)
                        time.sleep(2)
                        val = ''
                elif val.lower() == 'z':
                        stacking()
                        print_current_task("stack finished",1)
                        
        
        io.output(motor_enable_pin, False)
        # Program will cease all GPIO activity before terminating
        io.cleanup()
        
