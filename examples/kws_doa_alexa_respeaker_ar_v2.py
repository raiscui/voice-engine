"""
Record audio from a 6 microphone array, and then search the keyword "alexa".
After finding the keyword, Direction Of Arrival (DOA) is estimated.

Requirements:
    pip install voice-engine avs pixel_ring

Hardware:
    respeaker v2. 
"""
import pyaudio

import signal
import time
from voice_engine.element import Element

# from voice_engine.source import Source
from voice_engine.kws import KWS
from voice_engine.channel_picker import ChannelPicker
from voice_engine.doa_respeaker_v2_6mic_array import DOA
from avs.alexa import Alexa
from pixel_ring import pixel_ring
pixel_ring.change_pattern('echo')

pixel_ring.wakeup(0)
time.sleep(1)
pixel_ring.off()


class Source(Element):
    def __init__(self, rate=16000, frames_size=None, channels=6, device_name=''):

        super(Source, self).__init__()

        self.rate = rate
        self.frames_size = frames_size if frames_size else rate / 100
        self.channels = 6

        self.pyaudio_instance = pyaudio.PyAudio()

        device_index = None
        for i in range(self.pyaudio_instance.get_device_count()):
            dev = self.pyaudio_instance.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            print('{}:{} with {} input channels'.format(
                i, name, dev['maxInputChannels']))
            if name.find('ReSpeaker 4 Mic Array') >= 0 and dev['maxInputChannels'] == self.channels:
                device_index = i
                break

        if device_index is None:
            raise ValueError(
                'Can not find an input device with {} channel(s)'.format(self.channels))

        self.stream = self.pyaudio_instance.open(
            start=False,
            format=pyaudio.paInt16,
            input_device_index=device_index,
            channels=self.channels,
            rate=int(self.rate),
            frames_per_buffer=int(self.frames_size),
            stream_callback=self._callback,
            input=True
        )

    def _callback(self, in_data, frame_count, time_info, status):
        super(Source, self).put(in_data)

        return None, pyaudio.paContinue

    def start(self):
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()


def main():
    # src = Source(rate=16000, frames_size=320, channels=6)
    src = Source(rate=16000, frames_size=160, channels=6,
                 device_name='hw:1')

    ch0 = ChannelPicker(channels=src.channels, pick=0)
    kws = KWS(model='snowboy', sensitivity=0.5)
    # doa = DOA(rate=src.rate, chunks=20)
    alexa = Alexa()

    alexa.state_listener.on_listening = pixel_ring.listen
    alexa.state_listener.on_thinking = pixel_ring.think
    alexa.state_listener.on_speaking = pixel_ring.speak
    alexa.state_listener.on_finished = pixel_ring.off

    src.pipeline(ch0, kws, alexa)

    # src.link(doa)

    def on_detected(keyword):
        # direction = doa.get_direction()
        # print('detected {} at direction {}'.format(keyword, direction))
        print('detected {} '.format(keyword))
        alexa.listen()
        # pixel_ring.wakeup(direction)

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
