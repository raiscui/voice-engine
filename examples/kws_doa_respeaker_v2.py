"""
Record audio from a 6 microphone array, and then search the keyword "alexa".
After finding the keyword, Direction Of Arrival (DOA) is estimated.

Requirements:
    pip install voice-engine avs pixel_ring

Hardware:
    respeaker v2. 
"""

import signal
import time
from voice_engine.source import Source
from voice_engine.kws import KWS
from voice_engine.channel_picker import ChannelPicker
from voice_engine.doa_respeaker_v2_6mic_array import DOA
from pixel_ring import pixel_ring
import mraa

power = mraa.Gpio(12)
time.sleep(1)
power.dir(mraa.DIR_OUT)
power.write(0)

pixel_ring.wakeup(0)
time.sleep(1)
pixel_ring.off()


def main():
    src = Source(rate=16000, frames_size=320, channels=8)
    ch0 = ChannelPicker(channels=src.channels, pick=0)
    kws = KWS(model='snowboy', sensitivity=0.5)
    doa = DOA(rate=src.rate, chunks=20)

    src.pipeline(ch0, kws)

    src.link(doa)

    def on_detected(keyword):
        direction = doa.get_direction()
        print('detected {} at direction {}'.format(keyword, direction))
        pixel_ring.wakeup(direction)
        time.sleep(2)
        pixel_ring.off()

    kws.on_detected = on_detected

    is_quit = []

    def signal_handler(sig, frame):
        is_quit.append(True)
        print('quit')
    signal.signal(signal.SIGINT, signal_handler)

    src.pipeline_start()
    while not is_quit:
        time.sleep(1)

    src.pipeline_stop()


if __name__ == '__main__':
    main()
