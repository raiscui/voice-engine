import soundcard as sc
import time
import numpy
import datetime
import threading
import logging

from voice_engine.element import Element

speakers = sc.all_speakers()
default_speaker = sc.default_speaker()
mics = sc.all_microphones()
default_mic = sc.default_microphone()


class Source(Element):
    def __init__(self, rate=16000, frames_size=1280, channels=1, device_name='default', bits_per_sample=16):
        super(Source, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.mic = None
        self.rate = rate
        self.channels = channels
        self.done = False
        self.count = 0
        self.frames_size = frames_size

        if device_name:
            try:
                self.mic = sc.get_microphone(device_name)
            except Exception:
                self.logger.warn("can't get by device_name")
                self.mic = sc.default_microphone()
        else:
            self.mic = sc.default_microphone()

    def run(self):
        self.logger.warn('in run')
        self.logger.warn(self.mic.name)

        try:
            with self.mic.recorder(samplerate=self.rate, channels=self.channels) as mic:
                self.logger.warn('record now ')
                while not self.done:
                    data = mic.flush()
                    if len(data):
                        super(Source, self).put(data)
                    self.count = 0
                    while self.count < 1000 and not self.done:
                        data = mic.record(numframes=self.frames_size)
                        self.logger.debug(
                            'recorded frames:{}'.format(self.frames_size))
                        super(Source, self).put(data)

        except Exception as e:
            self.logger.error(e)

    def start(self):
        """Start a recording thread"""
        self.logger.warn('start')
        self.done = False
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop recording"""
        self.logger.warn('stop')

        self.done = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
