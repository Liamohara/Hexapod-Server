from adafruit_servokit import ServoKit


class Servo:
    def __init__(self):
        self.kit_40 = ServoKit(channels=16, address=0x40)
        self.kit_41 = ServoKit(channels=16, address=0x41)

    def setServoAngle(self, channel, angle):
        if channel < 16:
            self.kit_41.servo[channel].angle = angle
        elif channel >= 16 and channel < 32:
            channel -= 16
            self.kit_40.servo[channel].angle = angle
        else:
            print("Invalid servo angle. Must be 0-31.")

    def relax(self):
        for i in range(8):
            self.kit_41.servo[i+8].angle = None
            self.kit_40.servo[i].angle = None
            self.kit_40.servo[i+8].angle = None

########################################################

# Servo address and channel diagram
#       0x40 2    ##            ##   0x41 13
#        0x40 1    ## [Front]  ##   0x41 14
#         0x40 0    ############   0x41 15
#                  ##          ##
#                 ##            ##
# 40 5 4 3   #######              #######   0x41 12 11 10
#                 ##            ##
#                  ##          ##
#           0x40 6  ############   0x41 9
#          0x40 7  ##  [Rear]  ##   0x41 8
#        0x40 11  ##            ##   0x40 15


# setServoAngle() channel map diagram
#              [18] [Front]  [13]
#               [17]        [14]
#                [16]######[15]
#                ##          ##
#               ##            ##
#    [21][20][19]              [10][11][12]
#               ##            ##
#                ##          ##
#                [22]#######[9]
#               [23]         [8]
#              [27]  [Rear]   [31]

########################################################
