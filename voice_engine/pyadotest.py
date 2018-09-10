import pyaudio
import logging
import time
import time

logging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger(__file__)

pyaudio_instance = pyaudio.PyAudio()

device_index = pyaudio_instance.get_default_input_device_info()['index']
print(device_index)
print(pyaudio_instance.get_device_count())
for i in range(pyaudio_instance.get_device_count()):
    dev = pyaudio_instance.get_device_info_by_index(i)
    name = dev['name'].encode('utf-8')
    logger.info('{}:{} with {} input channels'.format(
        i, name, dev['maxInputChannels']))


a = 0


def _callback(in_data, frame_count, time_info, status):
    # print(frame_count)
    global a
    a += 1
    if a < 100:
        return None, pyaudio.paContinue

    else:
        global start_time
        end_time = time.time()
        print((end_time-start_time)-(1024*100/44100))
        return None, pyaudio.paAbort


stream = pyaudio_instance.open(
    start=False,
    format=pyaudio.paInt16,
    input_device_index=0,
    channels=2,
    rate=int(44100),
    frames_per_buffer=int(1024),
    stream_callback=_callback,
    input=True
)
stream.start_stream()
start_time = time.time()

while True:
    time.sleep(0.1)
    pass
