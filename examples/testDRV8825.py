#!/usr/bin/python
import sys
import time
import getopt
from steppermotor_precise import AutoDRV8825

# these are the GPIO pins the DRV8825 ports are tied to:
GPIOS = {
    "enable":23,
    "step":24,
    "direction":25,
    "m0":22,
    "m1":17,
    "m2":4
}

def print_help():
    print("test.py -s <steps> -f <frequency> -a <accel_microsteps> -m <stepsize_min> -n <stepsize_max> -v <verbosity>")
    print("test.py --steps <int> --frequency <int> --accel_microsteps <int> --stepsize_min <float> --stepsize_max <float> --verbosity <int>\n")
    print("<accel_microsteps> defines the number of microsteps for each acceleration speed")
    print("<stepsize_min> defines the minimum allowed step size")
    print("<stepsize_max> defines the maximum allowed step size")

if __name__ == "__main__":

    # default values
    steps = 250
    frequency = 1000
    accel_microsteps = 50
    stepsize_min = 1/32
    stepsize_max = 1
    vebosity = 0
    motor = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hs:f:a:m:n:v:",
		["steps=","frequency=","accel_microsteps=",
                 "stepsize_min=","stepsize_max=","verbosity="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-s", "--steps"):
            steps = int(arg)
        elif opt in ("-f", "--frequency"):
            frequency = int(arg)
        elif opt in ("-a", "--accel_microsteps"):
            accel_microsteps = int(arg)
        elif opt in ("-m", "--stepsize_min"):
            stepsize_min = float(arg)
        elif opt in ("-n", "--stepsize_max"):
            stepsize_max = float(arg)
        elif opt in ("-v", "--verbosity"):
            verbosity = int(arg)

    try:
        motor = AutoDRV8825(GPIOS, frequency, accel_microsteps=accel_microsteps, verbosity=verbosity)
        motor.enable()
        print("Requesting " + str(steps) + " steps...")
        madesteps = motor.auto_step(steps, stepsize_min=stepsize_min, stepsize_max=stepsize_max)
        print("Estimated number of whole steps: " + str(madesteps))
        print("Difference between requested and made steps: " + str(steps - madesteps))
        motor.disable()
    finally:
        if motor:
            motor.close()
