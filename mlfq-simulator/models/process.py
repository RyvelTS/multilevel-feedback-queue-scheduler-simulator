class Process:
    def __init__(self, process_id, burst_time):
        self.process_id = process_id
        self.burst_time = burst_time
        self.priority = 0
        self.entry_time = 0
        self.remaining_time_slice = None