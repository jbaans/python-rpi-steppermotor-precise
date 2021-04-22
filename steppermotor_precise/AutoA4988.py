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
from steppermotor_precise.A4988 import A4988

class AutoA4988(A4988):
    """
    This class extends the DRV8825 stepper motor driver class.
    It adds automatic acceleration and deceleration of the motor.
    """
    # number of microsteps for each acceleration step
    ACCEL_MICROSTEPS = 50

    def __init__(self, GPIOS, frequency, stepsize=None, verbosity=0, accel_microsteps=None):
        """Initialize the motor driver.
        Calls parent init function and sets number of acceleration microsteps per speed.

        Args:
            GPIOS (dict): dict of GPIO description: GPIO pin.
            frequency (int): PWM pulses per second.
            stepsize (int, optional): Microstep size. Defaults to None.
            verbosity (int, optional): Integer to set verbosity. Defaults to 0.
            accel_microsteps (int, optional): Number of acceleration microsteps
                                              per speed. Defaults to None.
        """
        print("Initializing Stepper Motor...")
        super().__init__(GPIOS, frequency, stepsize=stepsize, verbosity=verbosity)

        if accel_microsteps < 1:
            raise Exception("Error: Invalid number for acceleration microsteps: " + str(accel_microsteps))
        self.ACCEL_MICROSTEPS = accel_microsteps or self.ACCEL_MICROSTEPS
        if self.verbosity >= 1:
            print("Acceleration microsteps: " + str(self.ACCEL_MICROSTEPS))
        print("Initialization done.")


    def auto_step(self, steps, frequency=None, dutycycle=None,
                  stepsize_min=None, stepsize_max=None):
        """Make the specified number of steps with automatic acceleration
        and deceleration, count steps while doing so.

        Args:
            steps (float)): number of whole steps to make.
            frequency (int, optional): PWM frequency (Hz). Defaults to None.
            dutycycle (int, optional): PWM duty cycle 0..255 (for 0..100%). Defaults to None.
            stepsize_min (float): Minimum microstep size. Any of 1, 1/2, 1/4, 1/8,
                                  1/16 or None. Defaults to None.
            stepsize_max (float): Maximum microstep size. Any of 1, 1/2, 1/4, 1/8,
                                  1/16 or None. Defaults to None.

        Returns:
            float: (estimation of) step size that was made
        """
        def _accelerate(self, microsteps, stepsizes):
            """Accelerate (decelerate) by making series of microsteps with
            increasing (decreasing) stepsizes.

            Args:
                microsteps (int): number of microsteps to make for every stepsize
                stepsizes ([float]): ordered list of stepsizes to iterate

            Returns:
                float: (estimation of) step size that was made
            """
            subtotal = 0
            for stepsize in stepsizes:
                steps = stepsize * microsteps
                subtotal += self.step(steps, stepsize=stepsize)
            return subtotal

        def _stationary(self, steps):
            """Make the specified amount of whole steps

            Args:
                steps (float)): number of whole steps to make.

            Returns:
                float: (estimation of) step size that was made.
            """
            if self.verbosity >= 3:
                print("Requesting " + str(steps) + " more steps...")
            return self.step(steps)

        def _verbose(self, total):
            """Be verbose about number of steps"""
            if self.verbosity >= 3:
                print("Total number of whole steps is now " + str(total))

        # determine allowed stepsizes
        stepsizes = []
        for stepsize in reversed(list(self.STEPSIZE.keys())):
            if ((stepsize_min and stepsize >= stepsize_min) and
                (stepsize_max and stepsize <= stepsize_max)):
                stepsizes.append(stepsize)

        # accelerate in same direction as steps
        accel_microsteps = int(math.copysign(self.ACCEL_MICROSTEPS, steps))

        # check acceleration/decelation length
        acceleration_len = 0
        for stepsize in stepsizes:
            acceleration_len += stepsize * accel_microsteps
        if abs(2 * acceleration_len) > abs(steps):
            print("Acceleration is too long for the requested number of steps, aborting.")
            return 0

        # accelerate
        subtotal = 0
        subtotal += _accelerate(self, accel_microsteps, stepsizes)
        _verbose(self, subtotal)

        remainder = steps - (2 * subtotal)
        subtotal += _stationary(self, remainder)
        _verbose(self, subtotal)

        # decelerate with stepsizes reversed
        subtotal += _accelerate(self, accel_microsteps, reversed(stepsizes))
        _verbose(self, subtotal)

        remainder = steps - subtotal
        subtotal += _stationary(self, remainder)
        _verbose(self, subtotal)

        return subtotal
