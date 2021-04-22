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

import time
import sys
import pigpio as pigpio

class BasicDriver:
    """
    This class provides an interface for stepper motor drivers 
    connected to Raspberry Pi GPIO and uses the PIGPIO library to provide
    accurate PWM pulses to drive the (micro) steps.
    """
    WAIT_ENABLE = None      # seconds to stabilize after enable
    DEFAULT_DUTYCYCLE = 123 # 0..255
    GPIOS = {}              # dict of GPIO description: GPIO pin

    # default settings:
    direction = True        # rotation direction
    frequency = 0           # PWM pulses per second
    dutycycle = 0           # 0..255 for 0..100%
    gpio = None             # pigpio object
    verbosity = None        # integer to set verbosity

    def __init__(self, GPIOS, frequency, verbosity=0):
        """Initialize the motor driver.
        Sets verbosity, GPIO pins numbers, frequency.
        Connects to PIGPIO and configures GPIO.

        Args:
            GPIOS (dict): dict of GPIO description: GPIO pin.
            frequency (int): PWM pulses per second.
            verbosity (int, optional): integer to set verbosity. Defaults to 0.
        """

        def _get_key(val, dict):
            for key, value in dict.items():
                if val == value:
                    return key

        self.verbosity = verbosity
        self.GPIOS = GPIOS

        # init pigpio interface 'gpio'
        self.gpio = pigpio.pi()
        if not self.gpio.connected:
            print("Could not connect to PIGPIO daemon, is it running? Exiting.")
            exit()
        elif self.verbosity >= 1:
            print("Connected to PIGPIO daemon.")

        # init required gpio pins
        for g in list(self.GPIOS.values()):
            self.gpio.set_mode(g, pigpio.OUTPUT)
            if self.verbosity >= 1:
                print("GPIO " + _get_key(g, self.GPIOS) + " is set to pin " + str(g) )

        for g in list(self.GPIOS.values()):
            self.gpio.write(g, False)

        # set defaults
        self.set_direction(self.direction)
        self.set_frequency(frequency)
        if self.verbosity >= 1:
            print("Initial frequency: " + str(self.frequency))


    def close(self):
        """
        Set all GPIOs to low and disconnects from pigpio daemon
        """
        # Switch gpios off
        for g in list(self.GPIOS.values()):
            self.gpio.write(g, False)

        if self.verbosity >= 2:
            print("Set GPIOs to Low.")

        # Disconnect from PIGPIO daemon
        self.gpio.stop()
        print("Closed PIGPIO connection.")


    def set_direction(self, direction):
        """Sets direction GPIO pin

        Args:
            direction (bool): Rotation direction, True for clockwise
        """
        self.gpio.write(self.GPIOS['direction'], direction)
        self.direction = direction
        if self.verbosity >= 2:
            print("Set direction to " + str(direction))


    def set_frequency(self, frequency):
        """Sets PWM frequency

        Args:
            frequency (int): PWM frequency (Hz)

        Returns:
            actual_frequency (int): PWM frequency that is actually set by PIGPIO
        """
        if frequency < 1:
            raise Exception("Error: Invalid frequency: " + str(frequency))
        actual_freq = self.gpio.set_PWM_frequency(self.GPIOS['step'], frequency)
        self.frequency = actual_freq
        if self.verbosity >= 2:
            print("Frequency is set to " + str(actual_freq))
        return actual_freq


    def set_dutycycle(self, dutycycle):
        """Sets PWM duty cycle

        Args:
            dutycycle (int): PWM duty cycle 0..255 (for 0..100%)
        """
        self.gpio.set_PWM_dutycycle(self.GPIOS['step'], dutycycle)
        self.dutycycle = dutycycle
        if self.verbosity >= 3:
            print("Dutycycle is set to " + str(dutycycle))


    def enable(self, frequency=None, dutycycle=None, direction=None):
        """Enables motor driver chip by setting duty cycle nonzero.
        Requires some time to settle, set by WAIT_ENABLE.

        Args:
            frequency (int, optional): PWM frequency (Hz). Defaults to None.
            dutycycle (int, optional): PWM duty cycle 0..255 (for 0..100%). Defaults to None.
            direction (bool, optional): Rotation direction, True for clockwise. Defaults to None.
        """
        if frequency:
            self.set_frequency(frequency)
        if direction:
            self.set_direction(direction)
        time.sleep(self.WAIT_ENABLE)

        self.gpio.write(self.GPIOS['enable'], True)
        time.sleep(self.WAIT_ENABLE)

        print("Enabled motor.")


    def disable(self):
        """Disables motor driver chip by setting duty cycle to zero.
        Requires some time to settle, set by WAIT_ENABLE.
        """
        self.set_dutycycle(0)
        time.sleep(self.WAIT_ENABLE)

        self.gpio.write(self.GPIOS['enable'], False)
        time.sleep(self.WAIT_ENABLE)

        print("Disabled motor.")


    def pulse(self, pulses, frequency=None, dutycycle=None, direction=None):
        """Output the specified number of pulses to the motor driver chip
        at the specified frequency, with the specified duty cycle and in
        the specified direction.
        A nonzero PWM duty cycle will start the PWM pulse output.
        Calculates the time to wait to output the specified number of pulses,
        and waits this time while the PWM output is active, then sets the
        PWM duty cycle to zero.

        Args:
            pulses (int)): number of pulses to output to motor driver chip
            frequency (int, optional): PWM frequency (Hz). Defaults to None.
            dutycycle (int, optional): PWM duty cycle 0..255 (for 0..100%). Defaults to None.
            direction (bool, optional): Rotation direction, True for clockwise. Defaults to None.

        Returns:
            int: (estimated) number of pulses (steps) that were output
        """
        if pulses < 1:
            print("Number of pulses must be equal or larger than 1, received: " + str(pulses) + ", aborting.")
            return 0

        if direction is not None and not (self.direction == direction):
            self.set_direction(direction)

        if frequency:
            self.set_frequency(frequency)

        waittime = pulses / self.frequency
        if self.verbosity >= 3:
            print("Sending " + str(pulses) + " pulses...")

        # dutycycle > 0 is required to output pulses, use default if none was provided
        if not dutycycle:
            dutycycle = self.DEFAULT_DUTYCYCLE

        # setting duty cycle will start/stop the PWM output for stepping
        self.set_dutycycle(dutycycle)
        time.sleep(waittime)
        self.set_dutycycle(0)

        return pulses
