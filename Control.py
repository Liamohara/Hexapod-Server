# -*- coding: utf-8 -*-
from copy import deepcopy
from math import acos, atan2, cos, degrees, pi, radians, sin, sqrt
from numpy import matrix
from time import sleep

from Servo import Servo


class Control:
    def __init__(self):
        self.__SERVO_MANAGER = Servo()

        self.__L1 = 33
        self.__L2 = 90
        self.__L3 = 110

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

        self.__balance_leg_coords = matrix([
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40],
            [140, 0, -40]
        ])  # The position vector of each leg tip in the "balance" position.

        self.__calibrated_leg_coords = matrix([
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0],
            [140, 0, 0]
        ])

        self.__coord_offset = matrix([
            [-15, 55, 10],
            [0, 15, 0],
            [-8, 10, -30],
            [-15, 0, -15],
            [-15, 22, -21],
            [-15, 20, 10]
        ])  # A coordinate offset for each leg tip - accounting for the misalignment of each servo.

        self.__angles = matrix([
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0],
            [90, 0, 0]
        ])  # The angle of each servo.

        self.__setServos()

        sleep(.2)

        self.__walk(5, 135)

    def __setServos(self):
        if self.__inRangeOfMotion():
            self.__calibratePosition()  # Use self.__calibrated_position

            for leg in range(6):
                self.__angles[leg, 0], self.__angles[leg, 1], self.__angles[leg, 2] = self.__coordsToAngles(
                    self.__calibrated_leg_coords[leg, 0], self.__calibrated_leg_coords[leg, 1], self.__calibrated_leg_coords[leg, 2])

                if leg > 2:
                    for joint in range(3):
                        self.__angles[leg, joint] = 180 - \
                            self.__angles[leg, joint]

            for leg in range(6):
                for joint in range(3):
                    self.__SERVO_MANAGER.setAngle(
                        self.__servo_channels[leg, joint],
                        self.__restrict(self.__angles[leg, joint], 0, 180)
                    )

        else:
            print("Coordinate is not in effective range of motion")

    def __coordsToAngles(self, x, y, z):
        ###### Inverse Kinematics ######
        alpha = atan2(y, x)

        x_23 = sqrt(x**2 + y**2) - self.__L1
        epsilon = acos(
            (self.__L2**2 + self.__L3**2 - z**2 -
             x_23**2) / (2 * self.__L2 * self.__L3)
        )

        gamma = pi - epsilon
        beta = - atan2(z, x_23) - atan2(self.__L3*sin(epsilon),
                                        self.__L2 - self.__L3*cos(epsilon))

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
        self.__calibrated_leg_coords = self.__leg_coords + self.__coord_offset

    def __restrict(self, value, min, max):
        if value < min:
            return min
        elif value > max:
            return max
        else:
            return value

    def __balance(self):  #  TODO Save for API
        self.__leg_coords = deepcopy(self.__balance_leg_coords)

        self.__setServos()

    def __walk(self, paces, angle, precision=40):
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

        angle = angle - 360 * (abs(angle) // 360)

        x_dir = sin(radians(angle))
        y_dir = cos(radians(angle))

        if 90 > abs(angle) > 270:
            y_dir *= -1

        self.__balance()

        for _ in range(paces):
            step = int(80/precision)

            for distance in range(0, 80 + step, step):
                z = abs(40 * sin(9 * radians(distance) / 2)) - 40

                if distance <= 40:
                    x = distance * x_dir
                    y = distance * y_dir

                    self.__leg_coords[0] = [140 + x, y, z]
                    self.__leg_coords[2] = [140 + x, y, z]
                    self.__leg_coords[4] = [140 - x, y, z]

                    self.__setServos()
                else:
                    distance -= 40
                    x = distance * x_dir
                    y = distance * y_dir

                    self.__leg_coords[1] = [140 + x, y, z]
                    self.__leg_coords[3] = [140 - x, y, z]
                    self.__leg_coords[5] = [140 - x, y, z]

                    self.__setServos()

                sleep(.05)

            # Moves Hexapod into balance position SLOWLY so legs don't slip.
            coord_diff = self.__balance_leg_coords - self.__leg_coords

            for count in range(10, 0, -1):
                self.__leg_coords = self.__balance_leg_coords - count * coord_diff / 10

                self.__setServos()
                sleep(.05)

    # For API

    def __anglesToCoords(self, a, b, c):
        # Converting angles for use in forward kinematic calculations.
        alpha = pi/2 - radians(a)
        beta = radians(b) - pi/2
        gamma = radians(c) - pi/2

        ###### Forward Kinematics ######
        r = self.__l1 + self.__l2 * cos(beta) + self.__l3 * cos(beta + gamma)

        x = round(cos(alpha) * r)
        y = round(sin(alpha) * r)

        z = round(- self.__l3 * sin(beta + gamma) - self.__l2 * sin(beta))

        return x, y, z

# TODO Custom iterator
# TODO Singleton classes
# TODO Set height of body
