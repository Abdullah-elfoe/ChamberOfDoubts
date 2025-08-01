class Timer:
    def __init__(self, start_time, stop_time):
        self.start_time = start_time
        self.stop_time = stop_time
        self.pointer = self.start_time
        self.increment = 1
        self.paused = False
        self.ran = False

    @property
    def start(self):
        if self.pointer < self.stop_time:
            if not self.paused:
                self.pointer += self.increment
        else:
            self.reset
            
    @property
    def reset(self):
        self.pointer = self.start_time
        self.ran = True

    @property
    def pause(self):
        self.paused = True

    @property
    def play(self):
        self.paused = False

    @property
    def finished(self):
        if self.pointer == self.start_time and self.ran:
            return True
        