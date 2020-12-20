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
motor_is_enabled = 1

# CAMERA CONFIG
camera_trigger_pin = int(config['CAMERA']['camera_trigger_pin'])    # GPIO pin used to trigger the camera

camera_trigger_delay = float(config['CAMERA']['camera_trigger_delay'])          # The duration for the camera to detect it had been trigerred, reduce it if the camera take more picture than it should
camera_vibration_delay = float(config['CAMERA']['camera_vibration_delay'])      # The duration to wait for the all setup to stabilize to reduce moving blur
camera_taking_picture_delay = float(config['CAMERA']['camera_taking_picture_delay']) #Waiting for the camera to take a picture

double_shot_is_enabled = int(config['CAMERA']['double_shot_is_enabled']) # for the mirror lockup option

# STACKING CONFIG
number_of_step = int(config['STACKING']['number_of_step'])
current_position = 0
start_point = None
stop_point = None

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
# disable the motor, the motor will move freely
def stepper_enable():
    global motor_is_enabled
    if motor_is_enabled == 0:
        io.output(motor_enable_pin, False)
        motor_is_enabled = 1
        print_screen()
        print_current_task("motor enabled",1)
    else:
        io.output(motor_enable_pin, True)
        motor_is_enabled = 0
        print_screen()
        print_current_task("motor disabled",1)


def step_once():
    io.output(motor_step_pin, True)
    time.sleep(motor_delay)
    io.output(motor_step_pin, False)
    time.sleep(motor_delay)

def step_forward():
    global current_position
    io.output(motor_direction_pin, False)
    time.sleep(motor_delay)
    step_once()
    current_position += 1

def step_reverse():
    global current_position
    io.output(motor_direction_pin, True)
    time.sleep(motor_delay)
    step_once()
    current_position -= 1

# Full rotation forward, you need to configure the number of step in a 360 degree rotation
def rotate_forward():
    for x in range(0, pulses_per_rev):
            step_forward()
# Full rotation backward
def rotate_reverse():
    for x in range(0, pulses_per_rev):
            step_reverse()
            
def stepper_goto(aimed_position):
        global  current_position
        print_current_task('moving to start position', 0 )
        if aimed_position > current_position :
                while aimed_position != current_position + 1 :
                        step_forward()
        elif aimed_position < current_position :
                while aimed_position != current_position - 1 :
                        step_reverse()
        
        
        

# CAMERA FUNCTION
def take_picture():
    if double_shot_is_enabled == 1:
        io.output(camera_trigger_pin, True)
        time.sleep(camera_trigger_delay)
        io.output(camera_trigger_pin, False)
        time.sleep(camera_taking_picture_delay)
    time.sleep(camera_vibration_delay)
    io.output(camera_trigger_pin, True)
    time.sleep(camera_trigger_delay)
    io.output(camera_trigger_pin, False)

def stacking():
        global start_point
        global stop_point
        stepper_goto(start_point)
        print_current_task('stacking', 0 )
        
        number_of_shot = get_number_of_shot()
        
        if start_point < stop_point :
                for x in range(0, number_of_shot):
                    take_picture()
                    time.sleep(camera_taking_picture_delay)
                    print_current_task('stacking : picture ' + str(x + 1) + '/' + str(number_of_shot), 0 )
                    for y in range(0, number_of_step):
                        step_forward()
        elif start_point > stop_point :
                for x in range(0, number_of_shot):
                    take_picture()
                    time.sleep(camera_taking_picture_delay)
                    print_current_task('stacking : picture ' + str(x + 1) + '/' + str(number_of_shot), 0 )
                    for y in range(0, number_of_step):
                        step_reverse()

def set_start_point():
        global start_point
        start_point = current_position
        print_screen()
        print_current_task('Set start position', 1)
        
        
def set_stop_point():
        global stop_point
        stop_point = current_position
        print_screen()
        print_current_task('Set stop position', 1)
        

def get_number_of_shot():
        global start_point
        global stop_point
        global number_of_step
        if start_point == None or stop_point == None : # if one of the points is not set
                return 0
        else :
                return ( abs(start_point - stop_point) // number_of_step )


def double_shot_enable():
    global double_shot_is_enabled
    if double_shot_is_enabled == 1:
        double_shot_is_enabled = 0
        print_screen()
        print_current_task("double shot disabled",1)
    else:
        double_shot_is_enabled = 1
        print_screen()
        print_current_task("double shot enabled",1)

# BLESSED INTERFACE
# https://github.com/jquast/blessed
from blessed import Terminal

term = Terminal()

def print_screen():
        
        print(term.clear)
        
        print("      /\/\   ___| |_ ___  ___  _ __  / _| |_ __ _  ___| | __ " +  term.orange(" / _ \ / |"))
        print("     /    \ / _ | __/ _ \/ _ \| '__| \ \| __/ _` |/ __| |/ / " +  term.orange("| ' ' || |"))
        print("    / /\/\ |  __| ||  __| (_) | |    _\ | || (_| | (__|   <  " +  term.orange("| |_| ") + term.orangered("_") + term.orange("| |"))
        print(term.orangered("    \/    \/\___|\__\___|\___/|_|    \__/\__\__,_|\___|_|\_\ ") +  term.orange(" \___") +  term.orangered("(_") + term.orange("|_|"))
        print('===========================================================================')
        print(term.bold(" current task:") + term.move_x(38) + "|" + " number of shot: " + term.bold(str(get_number_of_shot())))
        print(term.move_x(38) + "|" + " number of step: " + term.bold(str(number_of_step)))
        print(term.move_x(38) + "|")
        print(term.move_x(38) + "|")
        print('===========================================================================')
        if motor_is_enabled == 0:
                print(' ' + term.bold('q') + ' quit | ' + term.bold('m') + ' enable motor')
        else:
                print(' ' + term.bold('q') + ' quit | ' + term.bold('m') + ' disable motor ')
        print(' ' + term.bold('r') + ' reverse step | ' + term.bold('f') + ' forward step | ' + term.bold('t') + ' reverse rotation | ' + term.bold('g') + ' forward rotation')
        if double_shot_is_enabled == 0:
                print(' ' + term.bold('s') + ' take a shot | ' + term.bold('d') + ' enable double shot')
        else:
                print(' ' + term.bold('s') + ' take a shot | ' + term.bold('d') + ' disable double shot')
        print(' ' + term.bold('z') + ' begin stacking! | ' + term.bold('y') + ' set start point | ' + term.bold('h') + ' set stop point')

        
def print_current_task(current_task, status):
        if status == 0 :
                print(term.move_y(7) + '                                      ' + term.move_x(1) + term.orange(current_task))
        else:
                print(term.move_y(7) + '                                      ' + term.move_x(1) + term.green(current_task))

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
                if val.lower() == 'r':# make a step backward
                        step_forward()
                        print_current_task("reverse step",1)
                elif val.lower() == 'f': # make a step forward
                        step_reverse()
                        print_current_task("forward step",1)
                elif val.lower() == 't': # make a 360 rotation backward
                        print_current_task("reverse rotation",0)
                        rotate_reverse()
                        print_current_task("reverse rotation",1)
                elif val.lower() == 'g': # make a 360 rotation backward
                        print_current_task("forward rotation",0)
                        rotate_forward()
                        print_current_task("forward rotation",1)
                elif val.lower() == 'm': # enable the stepper motor
                        stepper_enable()
                elif val.lower() == 's': # take a picture
                        take_picture()
                        print_current_task("took a shot",1)
                        time.sleep(2)
                        val = ''
                elif val.lower() == 'z': # start stacking
                        stacking()
                        print_current_task("stack finished",1)
                elif val.lower() == 'y': # set start point for stacking
                        set_start_point()
                elif val.lower() == 'h': # set stop point for stacking
                        set_stop_point()
                elif val.lower() == 'd': # trigger the camera twice for each picture for the mirror lockup option
                        double_shot_enable()

                        
        
        io.output(motor_enable_pin, False)
        # Program will cease all GPIO activity before terminating
        io.cleanup()
        
