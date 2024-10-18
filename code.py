# adaptationdu code # SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
                    # SPDX-License-Identifier: MIT

import time
import array
import math
import board
import audiobusio
import simpleio
import neopixel

#  innitialisation du bandeau de LEDs neopixel
pixel_pin = board.A0

pixel_num = 16

pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=0.1, auto_write=False)

#  function pour faire une moyenne des niveaux du micro
def mean(values):
    return sum(values) / len(values)

#  function qui retourne le niveau du micro
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))

#  initialisation du micro
mic = audiobusio.PDMIn(board.TX,
                       board.A1, sample_rate=16000, bit_depth=16)
samples = array.array('H', [0] * 160)

# variables pour ajuster les niveaux de magnitude
magnitudemin = 35
magnitudemax = 300

#  variable pour garder le niveau precedent du micro
last_input = 0

#  neopixel colors
GREEN = (0, 127, 0)
RED = (127, 0, 0)
YELLOW = (127, 127, 0)
OFF = (0, 0, 0)

#  tableau des couleurs pour le VU metre
colors = [GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, YELLOW, YELLOW,
          YELLOW, YELLOW, YELLOW, YELLOW, RED, RED, RED, RED]

#  on commence par eteindre les pixels
pixels.fill(OFF)
pixels.show()

while True:
    #  enregistrement de l'audio
    mic.record(samples, len(samples))
    #  magnitude contient la valeur du niveau du micro
    magnitude = normalized_rms(samples)
    #  decommenter pour voir la magnitude dans la console
    #print((magnitude,))
    if magnitude <= magnitudemin:
        magnitude = magnitudemin
    if magnitude > magnitudemax:
        magnitude = magnitudemax
    #  on mappe la plage de volume (magnitudemin - magnitudemax) sur les 16 neopixels
    mapped_value = simpleio.map_range(magnitude, magnitudemin, magnitudemax, 0, 16)
    input_val = int(mapped_value)

    #  si le niveau d'entree du micro a change depuis la derniere valeur...
    if last_input != input_val:
        #  Si le niveau est inferieur...
        if last_input > input_val:
            #  eteins les pixel non utilies
            for z in reversed(range(input_val, last_input)):
                pixels[z] = (OFF)
                pixels.show()
        else:
                #  allume les pixels en utilisant le tableau de couleurs
            for i in range(last_input, input_val):
                pixels[i] = (colors[i])
                pixels.show()
        #  mets a jour la valeur precedente
        last_input = input_val

    time.sleep(0.03)
