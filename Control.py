# -*- coding: utf-8 -*-
from math import acos, atan2, cos, degrees, pi, radians, sin, sqrt
from numpy import matrix
from time import sleep

from Servo import Servo


class Control:
    def __init__(self):
        self.__servoManager = Servo()

        self.__l1 = 33
        self.__l2 = 90
        self.__l3 = 110

        self.__servo_channels = matrix([
            [15, 14, 13],
            [12, 11, 10],
            [9, 8, 31],
            [22, 23, 27],
            [19, 20, 21],
            [16, 17, 18]
        ])  # The channel of each servo.

        self.__leg_coords = matrix([
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0]
        ])  # The position vector of each leg tip.

        self.__angles = matrix([
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0]
        ])  # The angle of each servo.

        self.__coord_offset = matrix([
            [-15, 55, 10],
            [0, 15, 0],
            [-8, 10, -30],
            [-15, 0, -15],
            [-15, 22, -21],
            [-15, 20, 10]
        ])  # A coordinate offset for each leg tip - accounting for the misalignment of each servo.

        self.__setServos()

        sleep(.2)

        self.__walk(10)

    def __setServos(self):
        if self.__inRangeOfMotion():
            self.__calibratePosition()  # Use self.__calibrated_position

            for leg in range(6):
                self.__angles[leg, 0], self.__angles[leg, 1], self.__angles[leg, 2] = self.__coordsToAngles(
                    self.__leg_coords[leg, 0], self.__leg_coords[leg, 1], self.__leg_coords[leg, 2])

                if leg > 2:
                    for joint in range(3):
                        self.__angles[leg, joint] = 180 - \
                            self.__angles[leg, joint]

            for leg in range(6):
                for joint in range(3):
                    self.__servoManager.setAngle(
                        self.__servo_channels[leg, joint],
                        self.__restrict(self.__angles[leg, joint], 0, 180)
                    )

        else:
            print("Coordinate is not in effective range of motion")

    def __coordsToAngles(self, x, y, z):
        ###### Inverse Kinematics ######
        alpha = atan2(y, x)

        x_23 = sqrt(x**2 + y**2) - self.__l1
        epsilon = acos(
            (self.__l2**2 + self.__l3**2 - z**2 -
             x_23**2) / (2 * self.__l2 * self.__l3)
        )

        gamma = pi - epsilon
        beta = - atan2(z, x_23) - atan2(self.__l3*sin(epsilon),
                                        self.__l2 - self.__l3*cos(epsilon))

        # Convert angles for use with servos
        a = round(degrees(pi/2 - alpha))
        b = round(degrees(pi/2 - beta))
        c = round(degrees(gamma))

        return a, b, c

    def __inRangeOfMotion(self):
        for leg in range(6):
            extension = sqrt(
                self.__leg_coords[leg, 0]**2 + self.__leg_coords[leg, 1]**2 + self.__leg_coords[leg, 2]**2)  # The distance from the base frame to the end effector.
            if extension < 90 or self.__leg_coords[leg, 0] < 0:
                return False

        return True

    def __calibratePosition(self):
        self.__leg_coords += self.__coord_offset

    def __restrict(self, value, min, max):
        if value < min:
            return min
        elif value > max:
            return max
        else:
            return value

    def __balance(self):  #  TODO Save for API
        self.__leg_coords = matrix([
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40]
        ])  # The position vector of each leg tip.
        self.__setServos()

    def __walk(self, paces):
        #############
        # The movement of the legs is modelled using a function of sine:
        #
        # y = | 40 * sin(9x/2) | - 40
        #
        #     0     20     40     80
        #   0 +---- ,-, --------- ,-
        #     |    /   \         /
        #     |   /     \       /
        #     |  /       \     /
        #     | /         \   /
        # -40 |/           '-'
        #
        #############

        precision = 40

        self.__balance()

        for _ in range(paces):
            step = int(80/precision)

            for y in range(0, 80 + step, step):
                z = abs(40 * sin(9 * radians(y) / 2)) - 40

                if y <= 40:
                    self.__leg_coords = matrix([
                        [140, y, z],
                        [140, 0, -40],
                        [140, y, z],
                        [140, 0, -40],
                        [140, y, z],
                        [140, 0, -40]
                    ])

                    self.__setServos()
                else:
                    y = y - 40
                    self.__leg_coords = matrix([
                        [140, 0, -40],
                        [140, y, z],
                        [140, 0, -40],
                        [140, y, z],
                        [140, 0, -40],
                        [140, y, z]
                    ])
                    self.__setServos()

                sleep(.05)

            sleep(4)
            self.__balance()

    # Saved for API

    # def __anglesToCoords(self, a, b, c):
    #     # Converting angles for use in forward kinematic calculations.
    #     alpha = pi/2 - radians(a)
    #     beta = radians(b) - pi/2
    #     gamma = radians(c) - pi/2

    #     ###### Forward Kinematics ######
    #     r = self.__l1 + self.__l2 * cos(beta) + self.__l3 * cos(beta + gamma)

    #     x = round(cos(alpha) * r)
    #     y = round(sin(alpha) * r)

    #     z = round(- self.__l3 * sin(beta + gamma) - self.__l2 * sin(beta))

    #     return x, y, z # TODO Save for API

# TODO Custom iterator
# TODO Singleton classes
