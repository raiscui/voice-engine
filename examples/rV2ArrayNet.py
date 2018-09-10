
import pyaudio

import signal
import time
from voice_engine.element import Element

from voice_engine.pyaudio_source import Source
from voice_engine.kws import KWS
from voice_engine.channel_picker import ChannelPicker
from voice_engine.doa_respeaker_v2_6mic_array import DOA
from voice_engine.netT import NetT
import logging
from avs.alexa import Alexa
from pixel_ring import pixel_ring
pixel_ring.change_pattern('echo')

pixel_ring.wakeup(0)
time.sleep(1)
pixel_ring.off()


def main():
    logging.basicConfig(level=logging.WARNING)
    # logging.basicConfig(level=logging.WARNING)

    logging.getLogger('hpack.hpack').setLevel(logging.INFO)
    # logging.getLogger('voice_engine.netT').setLevel(logging.DEBUG)

    # src = Source(rate=16000, frames_size=320, channels=6)
    src = Source(rate=16000, frames_size=128, channels=6,
                 device_name='ReSpeaker 4 Mic Array')

    ch0 = ChannelPicker(channels=src.channels, pick=0)
    nett = NetT()
    src.pipeline(ch0, nett)

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
