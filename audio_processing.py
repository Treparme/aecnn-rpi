#!/usr/bin/env python

"""
Real-time single-channel denoising using AECNN speech enhancement model and jackd audio server

The AECNN model needs to be able to execute within the required processing time (framesize/fs), 
otherwise xrun errors are produced by the jackd audio server and the output gets filled with random values.

If you are unsure of your model's capabilities, you can run the benchmark script and measure its execution time.

Fotis Drakopoulos, UGent
"""

from __future__ import division, print_function
from time import time
import jack
import sys
import numpy as np
from argparse import ArgumentParser
from threading import Event
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.x
from subprocess import check_call

def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-n", "--framesize", help="Size of the input/output frames of the model", required=True, type=int)
    parser.add_argument("-b", "--buffersize", help="Percentage of buffering in the input/output frames for reducing latency - can be 0, 0.5 or 0.75 (0, 1 or 3 buffers)", default=0, type=float)
    parser.add_argument("-o", "--overlap", help="Overlap percentage of the audio frames - can be 0 or 0.5", default=0, type=float)
    parser.add_argument("-q", "--queuesize", help="Size of the input/output queues in buffers", default=4, type=int)
    parser.add_argument("-p", "--precision", help="Float precision of the model", default='float32', type=str)
    parser.add_argument("-fs", "--sampling_rate", help="16 kHz sampling rate is used for AECNN models by default", default=16000, type=int)
    parser.add_argument("-s", "--summary", help="Print summary of the model", default=0, type=bool)

    return parser

def print_error(*args):
    print(*args, file=sys.stderr)

def xrun(delay):
    print_error("An xrun occured, increase JACK's period size?")

def shutdown(status, reason):
    print_error('JACK shutdown!')
    print_error('status:', status)
    print_error('reason:', reason)
    event.set()

def stop_callback(msg=''):
    if msg:
        print_error(msg)
    for port in client.outports:
        port.get_array().fill(0)
    event.set()

def process(frames):
    if frames != blocksize:
        stop_callback('blocksize must not be changed, I quit!')
    try:
        datain=client.inports[0].get_array()
        qin.put(datain)
        data = qout.get_nowait()
        client.outports[0].get_array()[:] = data
    except queue.Empty:
        stop_callback('Buffer is empty: increase queuesize?')


args = build_argparser().parse_args() #parse arguments

# Start jackd server
overlap = args.overlap
buffersize = args.buffersize
fs = args.sampling_rate
blocksize = int((1-overlap) * (1-buffersize) * args.framesize)
#command = 'sh start_jackd.sh %d %d' % (blocksize,fs)
command = 'sh start_jackd.sh 1024 16000'                                   
check_call(command.split()) # calls start_jackd script to start jackd server

# Use queues to pass data to/from the audio backend
if args.queuesize < 1:
    print('Queuesize must be at least 1')
    queuesize = 1
else:
    queuesize = args.queuesize
qout = queue.Queue(maxsize=queuesize)
qin = queue.Queue(maxsize=queuesize)
event = Event()

# Initialise variables
precision = 'float32'
model_blocksize = args.framesize
if buffersize != 0 or overlap != 0:
    buffer_blocksize = int(model_blocksize - blocksize)
    if overlap != 0:
        cleanb=np.zeros((blocksize,),dtype='float32')
noisy=np.zeros((1,model_blocksize,1),dtype=precision)
data=np.zeros((blocksize,),dtype=precision)

try:
    # Initialise jackd client
    client = jack.Client("thru_client")
    blocksize = client.blocksize
    samplerate = client.samplerate
    client.set_xrun_callback(xrun)
    client.set_shutdown_callback(shutdown)
    client.set_process_callback(process)

    client.inports.register('in_{0}'.format(1))
    client.outports.register('out_{0}'.format(1))
    i=client.inports[0]
    capture = client.get_ports(is_physical=True, is_output=True)
    playback = client.get_ports(is_physical=True, is_input=True, is_audio=True)
    o=client.outports[0]

    timeout = blocksize / samplerate
    print("Processing input in %d ms frames" % (int(round(1000 * timeout))))

    # Pre-fill queues
    #qin.put_nowait(data)
    qout.put_nowait(data) # the output queue needs to be pre-filled

    with client:
        i.connect(capture[0])
        # Connect mono file to stereo output
        o.connect(playback[0])
        o.connect(playback[1])
        
        datain=qin.get()
        
        dataout = datain*2
        
        qout.put(dataout)
        
except (queue.Full):
    raise RuntimeError('Queue full')
except KeyboardInterrupt:
    print('\nInterrupted by User')
command = 'killall jackd'
check_call(command.split())
