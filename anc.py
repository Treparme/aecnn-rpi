import numpy as np

class ANC():

    def __init__(self, qout, qout1, qin, qin1, delay, blocksize):
        self.epsilon = 10**(-3)
        self.delay = delay
        self.blocksize = blocksize
        self.noise = qin
        self.error = qin1
        self.antinoise = qout
        self.dummy_out = qout1

        self.mu = 1/delay #learning rate
        self.buffersize = self.blocksize
        self.multiplicator = 4
        self.windowsize = self.multiplicator * self.buffersize

        self.buffered_window = np.zeros(self.delay + self.windowsize + self.buffer_size)
        self.filter_ = np.zeros(self.windowsize)
        # self.filter_ = np.random.rand(windowsize) / 10
        self.leeg = np.zeros(buffersize)


    def start(self):
        while(True):
            noise = self.noise.get()
            error = self.error.get()

            output = self.anc_buffered(noise, error)

            self.output.put(output)
            self.dummy_out.put(self.leeg)


    def anc_buffered(self, noise, error):
        # buffer doorschuiven: eerste stuk wegwerpen en noise input vanachter aan plakken
        self.buffered_window[: -self.buffer_size] = self.buffered_window[self.buffer_size: ]
        self.buffered_window[-self.buffer_size: ] = noise

        self.error = error

        return calculate_antinoise_sample(np.arange(self.buffer_size)) # antinoise for each index


    def calculate_antinoise_sample(self, index):
        window = buffered_window[self.delay + index: self.delay + self.windowsize + index]
        antinoise_sample = - np.dot(window, self.filter_)
        self.update_filter(index)
        return antinoise_sample


    def update_filter(self, index):
        window_delay = buffered_window[index: self.windowsize + index]
        window_delay_normed = window_delay / (np.dot(window_delay, window_delay) + self.epsilon)
        self.filter_ += mu * self.error[index] * window_delay_normed

        # explosion protection
        if np.sum(abs(filter_)) > self.windowsize / 100:
            filter_ = np.zeros(self.windowsize)
