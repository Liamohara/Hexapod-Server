from adafruit_servokit import ServoKit


class Servo:
    def __init__(self):
        self.kit_40 = ServoKit(channels=16, address=0x40)
        self.kit_41 = ServoKit(channels=16, address=0x41)

    def get_servo_position(self, channel):
        if channel < 16:
            b = self.kit_41.servo[channel].angle
        elif channel >= 16 and channel < 32:
            channel -= 16
            b = self.kit_40.servo[channel].angle
        return b


S = Servo()

for channel in [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 31]:
    print(channel, S.get_servo_position(channel))
