import subprocess
import threading
import time

cmd = [
    'arecord',
    '-t', 'raw',
    '-f', 'S16_LE',
    '-c', '2',
    '-r', '44100',
    '-D', 'default',
    '-q'
]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
frames_bytes = int(1024 * 2*2)

t = 1024*100/44100
a = 0
start_time = time.time()

while a <= 100:
    a += 1
    audio = process.stdout.read(frames_bytes)
    # print(len(audio)/4)


end_time = time.time()
print((end_time-start_time)-(1024*100/44100))
