import soundcard as sc
import time
import numpy
import datetime
import threading

from voice_engine.element import Element

speakers = sc.all_speakers()
default_speaker = sc.default_speaker()
mics = sc.all_microphones()
default_mic = sc.default_microphone()


class Source(Element):
    def __init__(self, rate=16000, frames_size=None, channels=1, device_name='default', bits_per_sample=16):
        super(Source, self).__init__()
        self.mic = None
        self.rate = rate
        self.channels = channels
        self.done = False
        self.count = 0

        if device_name:
            try:
                self.mic = sc.get_microphone(device_name)
            except Exception:
                self.mic = sc.default_microphone()

    def run(self):
        try:
            with self.mic.recorder(samplerate=self.rate, channels=self.channels) as mic:
                while not self.done:
                    data = mic.flush()
                    super(Source, self).put(data)
                    self.count = 0
                    while self.count < 1000 and not self.done:
                        data = mic.record(numframes=1024)
                        super(Source, self).put(data)

        except Exception as e:
            print(e)

    def start(self):
        """Start a recording thread"""
        self.done = False
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop recording"""
        self.done = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
