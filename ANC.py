class ANC():

    def calculate_antinoise(self, noise_input, error_input):
        output = np.zeros(self.buffer_size)

        self.buffered_window[-self.buffer_size: ] = noise_input

        for index in range(self.buffer_size):
            window = buffered_window[self.delay + index: self.delay + self.windowsize + index]

            output[index] = - np.dot(window, self.filter_)

            error = error_input[index]
            window_delay = buffered_window[index: self.windowsize + index]
            window_delay_normed = window_delay / (np.dot(window_delay, window_delay) + self.epsilon)
            self.filter_ += mu * error * window_delay_normed

            # explosion protection
            if np.sum(abs(filter_)) > self.windowsize / 100:
                filter_ = np.zeros(self.windowsize)

        buffered_window[: -self.buffer_size] = buffered_window[self.buffer_size: ]
        return output


    def __init__(self, qout, qout1, qin, qin1, delay, blocksize):
        epsilon = 10**(-3)
        self.noise = qin
        self.error = qin1
        self.antinoise = qout
        self.dummy_out = qout1

        self.mu = 1/delay #learning rate
        self.buffersize = self.blocksize
        self.multiplicator = 4
        self.windowsize = self.multiplicator *self.buffersize

        self.buffered_window = np.zeros(self.delay + self.windowsize + self.buffer_size)
        self.filter_ = np.zeros(self.windowsize)
        # self.filter_ = np.random.rand(windowsize) / 10
        self.leeg = np.zeros(buffersize)


    def start(self):
        while(True):
            noise = self.noise.get()
            error = self.error.get()

            output = self.calculate_antinoise(noise, error)

            self.output.put(output)
            self.dummy_out.put(self.leeg)
