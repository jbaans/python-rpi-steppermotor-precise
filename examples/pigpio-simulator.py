#!/usr/bin/python
""" Dummy module for pigpio """
OUTPUT = True

class pi:
    """ Dummy class for simulating pigpio functions """
    connected = False

    def __init__(self, *args):
        self.connected = True
        print("Warning: Loaded dummy pigpio module!")

    def stop(self):
        pass

    def set_mode(self, *args):
        pass

    def write(self, *args):
        pass

    def set_PWM_dutycycle(self, *args):
        pass

    def set_PWM_frequency(self, pin, freq, *args):
        return freq
