Description
-----------
Provides the classes BasicDriver, DRV8825, AutoDRV8825, A4988and AutoA4988
to interface with the respective driver chip by means of the python [pigpio package](https://pypi.org/project/pigpio/).

Intended users: Developers.

This package provides an interface for stepper motor drivers connected to 
Raspberry Pi GPIO and uses the PIGPIO library to provide accurate PWM 
pulses to drive the (micro) steps.

It allows for setting microstep size, specifying WAIT_ENABLE time
and an appropriate DEFAULT_DUTYCYCLE and defining the allowed microstep
sizes.

It provides the step() function which allows for making a step with
the size of any multiple of the specified microstep size.

It provides automatic acceleration and deceleration of the motor with the 
auto_step() function in the AutoDRV8825 and AutoA4988 classes.

It provides the pulse() function to simply output pulses to the configured
driver chip.

See testDRV8825.py and testA4988.py for example code.

Requirements
------------
Steppermotor_precise requires both the pigpio daemon and the pigpio package for python to be installed.
See [here](http://abyz.me.uk/rpi/pigpio/download.html) for installation instructions.
Armv6 like the early Raspberry Pi and Pi Zero may require compiling from source (git).

Note: Before running steppermotor_precise the pigpio daemon must be started with

`sudo pigpiod`


Installation
------------
To install this package from github, you need to clone the repository:

`git clone https://github.com/jbaans/python-rpi-steppermotor-precise`

Then run the setup.py file from the cloned directory:

`sudo python setup.py install`

Usage
-------------
Make sure you set the GPIO pin numbers using the GPIOS {} dict. Refer to Raspberry Pi 
and DRV8825/A4988 datasheets for numbering details. For example:

`GPIOS = {
    "enable":23,
    "step":24,
    "direction":25,
    "m0":22,
    "m1":17,
    "m2":4
}`

Set PWM frequency (Hz) for stepper driver to run at:

    frequency = 1000

Create a motor object:

    try:
    
        motor = AutoDRV8825(GPIOS, frequency)
        
Enable the motor and run some steps (this will accelerate with microsteps):
        
        motor.enable()
        
        madesteps = motor.auto_step(steps)

        motor.disable()
    
Clean up the motor object:
        
    finally:
    
        if motor:
        
            motor.close()


