import numpy as np

class ANC():

    def __init__(self, qout, qout1, qin, qin1, delay, blocksize):
        self.noise_buffer = qin
        self.error_buffer = qin1
        self.output_buffer = qout
        self.dummy_output_buffer = qout1

        self.update_period = 20
        self.epsilon = 10**(-3)
        self.delay = delay
        self.blocksize = blocksize

        self.counter = 0

        self.mu = 1/delay #learning rate
        self.buffer_size = self.blocksize
        self.multiplicator = 4
        self.windowsize = self.multiplicator * self.buffer_size
        self.buffered_window = np.zeros(self.delay + self.windowsize + self.buffer_size)
        self.filter_ = np.zeros(self.windowsize)
        # self.filter_ = np.random.rand(windowsize) / 10
        self.leeg = np.zeros(self.buffer_size)


    def start(self):
        while(True):
            noise = self.noise_buffer.get()
            error = self.error_buffer.get()

            output = self.anc_buffered(noise, error)

            self.output_buffer.put(output)
            self.dummy_output_buffer.put(self.leeg)


    def anc_buffered(self, noise, error):
        # buffer doorschuiven: eerste stuk wegwerpen en noise input vanachter aan plakken
        self.buffered_window[: -self.buffer_size] = self.buffered_window[self.buffer_size: ]
        self.buffered_window[-self.buffer_size: ] = noise

        self.error = error
        print("printing first value of error so you can see results visually", error[0])

        return np.array([self.calculate_antinoise_sample(index) for index in range(self.buffer_size)]) # antinoise for each index


    def calculate_antinoise_sample(self, index):
        window = self.buffered_window[self.delay + index: self.delay + self.windowsize + index]
        antinoise_sample = - np.dot(window, self.filter_)
        self.update_filter(index)
        return antinoise_sample


    def update_filter(self, index):
        self.counter = (self.counter + 1) % self.update_period
        if self.counter == 0:
            window_delay = self.buffered_window[index: self.windowsize + index]
            window_delay_normed = window_delay / (np.dot(window_delay, window_delay) + self.epsilon)
            self.filter_ += self.mu * self.error[index] * window_delay_normed

        # explosion protection
        if np.sum(abs(self.filter_)) > self.windowsize / 100:
            self.filter_ = np.zeros(self.windowsize)
