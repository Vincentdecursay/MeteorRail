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
- Execute meteor_stack

## Developement
In /code
### Prerequies
- **Blessed** for the user interface: https://github.com/jquast/blessed
- **Cython** for the compilation

### Compilation
Just execute **compile.sh**
