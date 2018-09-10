import soundcard as sc
import time

import datetime

speakers = sc.all_speakers()
default_speaker = sc.default_speaker()
mics = sc.all_microphones()
default_mic = sc.default_microphone()


import numpy

print(default_speaker)
print(default_mic)

default_speaker.channels
# record and play back one second of audio:
# start_time = datetime.datetime.now()

# data = default_mic.record(samplerate=44100, numframes=44100)

# end_time = datetime.datetime.now()

# interval = (end_time-start_time).seconds  # 以秒的形式

# print(interval)


# default_speaker.play(data/numpy.max(data), samplerate=44100)

# alternatively, get a `recorder` and `player` object and play or record continuously:
start_time = time.time()
try:
    with default_mic.recorder(samplerate=44100) as mic, default_speaker.player(samplerate=44100) as sp:
        for _ in range(100):
            data = mic.record(numframes=1024)
            # data = mic.flush()

            # time.sleep(1024/44100)
            #
            # print('1')
            # sp.play(data)
        data = mic.flush()
        print(len(data))
except Exception as identifier:
    print(identifier)
    pass


end_time = time.time()
print((end_time-start_time)-(1024*100/44100))
