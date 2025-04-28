from .process import Process

class Queue:
    def __init__(self, priority):
        self.priority = priority
        self.processes = []

    def enqueue(self, process:Process, current_time):
        process.priority = self.priority
        process.entry_time = current_time
        self.processes.append(process)

    def dequeue(self):
        return self.processes.pop(0) if self.processes else None

    def is_empty(self):
        return len(self.processes) == 0