#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = "Jan Bonne Aans"
__copyright__ = "Copyright 2021, Jan Bonne Aans"
__credits__ = []
__license__ = "GPLv3"
__version__ = "1"
__maintainer__ = "Jan Bonne Aans"
__email__ = "jbaans-at-gmail.com"
__status__ = "Development"

import math
from steppermotor_precise.BasicDriver import BasicDriver

class A4988(BasicDriver):
    """
    This class extends the BasicDriver class to implement the A4988
    driver chip.
    It allows for setting microstep size, specifies WAIT_ENABLE time
    and an appropriate DEFAULT_DUTYCYCLE and defines the allowed microstep
    sizes.
    It provides the step() function which allows for making a step with
    the size of any multiple of the specified microstep size.
    """
    # dict with number of steps per step versus their mode/pin configurations
    STEPSIZE = {1:[0, 0, 0],
                1/2:[1, 0, 0],
                1/4:[0, 1, 0],
                1/8:[1, 1, 0],
                1/16:[0, 0, 1]}

    WAIT_ENABLE = 0.05       # sets seconds for A4988 to stabilize
    DEFAULT_DUTYCYCLE = 25   # 0..255

    # default settings:
    stepsize = 1

    def __init__(self, GPIOS, frequency, stepsize=None, verbosity=0):
        """Initialize the motor driver.
        Calls parent init function and sets microstep size.

        Args:
            GPIOS (dict): dict of GPIO description: GPIO pin.
            frequency (int): PWM pulses per second.
            stepsize (int, optional): Microstep size. Defaults to None.
            verbosity (int, optional): Integer to set verbosity. Defaults to 0.
        """
        super().__init__(GPIOS, frequency, verbosity=verbosity)

        # set defaults
        self.set_stepsize(stepsize or self.stepsize)
        if self.verbosity >= 1:
            print("Initial step size: " + str(self.stepsize))
            print("Default duty cycle (actual = 0): " + str(self.DEFAULT_DUTYCYCLE))


    def set_stepsize(self, size):
        """Sets microstep size.

        Args:
            size (float): Microstep size. Any of 1, 1/2, 1/4, 1/8 or 1/16.
        """
        if not size in self.STEPSIZE:
            raise Exception("Error: Invalid step size: " +str(size))
        self.gpio.write(self.GPIOS['m0'], self.STEPSIZE[size][0])
        self.gpio.write(self.GPIOS['m1'], self.STEPSIZE[size][1])
        self.gpio.write(self.GPIOS['m2'], self.STEPSIZE[size][2])
        self.stepsize = size
        if self.verbosity >= 3:
            print("Step size is set to " + str(size))


    def enable(self, frequency=None, dutycycle=None, stepsize=None, direction=None):
        """Sets step size. Then enables motor driver chip by calling parent function.

        Args:
            frequency (int, optional): PWM frequency (Hz). Defaults to None.
            dutycycle (int, optional): PWM duty cycle 0..255 (for 0..100%). Defaults to None.
            stepsize (float): Microstep size. Any of 1, 1/2, 1/4, 1/8 or 1/16.
            direction (bool, optional): Rotation direction, True for clockwise. Defaults to None.
        """
        if stepsize:
            self.set_stepsize(stepsize)

        super().enable(frequency=frequency, dutycycle=dutycycle, direction=direction)


    def step(self, steps, frequency=None, dutycycle=None, stepsize=None):
        """Make the specified amount of whole steps at the specified frequency, 
        with the specified duty cycle and in the specified direction, or their
        current values.
        Allows for making a step with the size of any multiple of the specified 
        microstep size.
        Calls the pulse() function to output the required number of pulses.

        Args:
            steps (float)): number of whole steps to make.
            frequency (int, optional): PWM frequency (Hz). Defaults to None.
            dutycycle (int, optional): PWM duty cycle 0..255 (for 0..100%). Defaults to None.
            stepsize (float, optional): Microstep size. Any of 1, 1/2, 1/4, 1/8, 1/16
                                        or None. Defaults to None.

        Returns:
            float: (estimation of) step size that was made
        """
        if stepsize:
            self.set_stepsize(stepsize)

        if steps < 0:
            direction = False
        else:
            direction = True

        # can only make whole positive number of pulses
        pulses = int(abs(steps) / self.stepsize)
        stepsmade = super().pulse(pulses, frequency=frequency, dutycycle=dutycycle,
                                  direction=direction) * self.stepsize
        # return the amount of steps made, with the sign of the requested direction
        return math.copysign(stepsmade, steps)
