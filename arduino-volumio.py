from nanpy import (ArduinoApi, SerialManager)
from time import sleep
from volumio import Volumio

connection = SerialManager()
ard = ArduinoApi(connection=connection)

v = Volumio()

vol_pin = 1
freq_pin = 0

volume = 0
old_rad = 0

playing_uri = ""

radios = v.radios()
radios_uri = [r["uri"] for r in radios]

def normalize_volume(vol, step=5):
    return int((vol / 1023) * (100/step)) * step

def normalize_radios(val):
    return int((val / 1023) * (len(radios) + 1))

while True:
    old_volume = volume
    volume = normalize_volume(ard.analogRead(vol_pin))

    rad = normalize_radios(ard.analogRead(freq_pin))

    playing_uri = v.playing_uri()

    if rad < len(radios):
        playing_uri = v.playing_uri()
        desired_uri = radios[rad]["uri"]

        if playing_uri != desired_uri or playing_uri == "":
            v.play_radio(desired_uri)
    else:
        if playing_uri in radios_uri:
            v.stop()
            print("Stopped radio")
        print("No radio")

    if old_volume != volume:
        v.set_volume(volume)

    print("Volume :", volume, " - Radio :", playing_uri)

    sleep(.1)