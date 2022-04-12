# -*- coding: utf-8 -*-
from math import acos, atan2, cos, degrees, pi, radians, sin, sqrt
from numpy import matrix

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
            [143, 0, -90],
            [143, 0, -90],
            [143, 0, -90],
            [143, 0, -90],
            [143, 0, -90],
            [143, 0, -90]
        ])  # The position vector of each leg tip.

        self.__angles = matrix([
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0]
        ])  # The angle of each servo.

        # self.__coord_offset = matrix([
        #     [83, -165, -169],
        #     [-4, -169, -154],
        #     [-36, -144, -138],
        #     [140, -26, -14],
        #     [40, 0, -20],
        #     [42, -11, -33]
        # ])  # A coordinate offset for each leg tip - accounting for the misalignment of each servo.

        self.__coord_offset = matrix([
            [-18, 50, -5],
            [0, 15, 0],
            [0, 10, 20],
            [0, 5, 0],
            [-15, 22, 0],
            [-10, 10, -20]
        ])  # A coordinate offset for each leg tip - accounting for the misalignment of each servo.

        self.__setServos()

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
        beta = atan2(z, x_23) - atan2(self.__l3*sin(epsilon),
                                      self.__l2 - self.__l3*cos(epsilon))

        print(beta)

        # Convert angles for use with servos
        a = round(degrees(pi/2 - alpha))
        b = round(degrees(pi/2 - beta))
        c = round(degrees(gamma))

        print(beta)

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

    # Saved for API

    # def __balance(self): # TODO Save for API
    #     self.__leg_coord = matrix([
    #         [140, 0, 0],
    #         [140, 0, 0],
    #         [140, 0, 0],
    #         [140, 0, 0],
    #         [140, 0, 0],
    #         [140, 0, 0]
    #     ])  # The position vector of each leg tip.

    #     self.__setServos()

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
