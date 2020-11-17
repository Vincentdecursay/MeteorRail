# MeteorStack
Motorized stacking rail project for micro and macrophotograhy, controlled by a Raspberry Pi.

# Hardware
## Components
- **Raspberry Pi**
- **DM556 motor controller** or an equivalent
- **Nema 17 stepper motor** or an equivalent
- **24 Volt power supply** for the motor controller
- **Power jack female connector**
- **4x 1k Ohm resistors** can depend of the transistor you use
- **4x BC547B NPN transistors** most NPN transitor can fit the bill
- **1x 100 Ohm resistor** can depend of the optocoupler you use
- **1x KB 814 DIP-4 optocoupler**
- **2.5mm jack cable** to trigger the camera
- **2.5mm jack female connector** 

## Schematic
![Image of schematic](https://github.com/Vincentdecursay/MeteorStack/blob/main/hardware/hardware_schematic.png)
**Dont forget to configure your motor controller with the right current for your stepper motor**

# Software
## Usage
In /software
- Configuration in config.txt
``` python
[STEPPER_MOTOR]
motor_enable_pin = 17 # GPIO pins
motor_direction_pin = 27
motor_step_pin = 22
motor_delay = 3E-004
# Number of pulses needed to do one revolution, can be changed with the motor controller
pulses_per_rev = 400

[CAMERA]
# GPIO pin
camera_trigger_pin = 23
camera_trigger_delay = 0.2 # the time needed for the camera to detect that it had been triggered. Keep it as low as possible
camera_vibration_delay = 1 # delay for the all rail setup to stabilize before taking a picture
camera_taking_picture_delay = 0.2 # delay to let the camera take the picture before moving again during stacking

[STACKING]
number_of_shot = 10 # Number of pictures taken during a stack
number_of_step = 2 # Number of steps done for each picture taken
```
- Execute meteor_stack

## Developement
In /code
### Prerequies
- **Blessed** for the user interface: https://github.com/jquast/blessed
- **Cython** for the compilation

### Compilation
Just execute **compile.sh**
