from numpy import array

from Servo import Servo

channels = array([
    [15, 14, 13],
    [12, 11, 10],
    [9, 8, 31],
    [22, 23, 27],
    [19, 20, 21],
    [16, 17, 18]
])

for channel in channels.flatten():
    Servo().relax(channel)
