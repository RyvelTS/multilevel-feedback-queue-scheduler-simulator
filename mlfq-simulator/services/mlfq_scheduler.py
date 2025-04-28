from ..models.queue import Queue
from .queue_service import QueueService
import time

class MLFQ:
    def __init__(self, root, processes, time_quantum, promotion_threshold,
                 visualizer, num_queues=3):
        self.root = root
        self.processes = processes
        self.queues = [Queue(i) for i in range(num_queues)]
        self.queue_service = QueueService(self.queues)
        self.visualizer = visualizer
        self.time_quantum = time_quantum
        self.promotion_threshold = promotion_threshold

    def run(self):
        # Enqueue all processes in the highest priority queue (queue 0)
        for p in self.processes:
            self.queues[0].enqueue(p, 0)

        current_time = 0
        self.queue_service.print_queues(current_time)
        self.visualizer.assign_colors(self.processes)
        self.visualizer.save_queue_image(self.queues, current_time)

        while any(not q.is_empty() for q in self.queues):
            # Promote processes that have waited too long
            self.queue_service.promote_processes(current_time, self.promotion_threshold)

            processed = False
            for i, queue in enumerate(self.queues):
                if not queue.is_empty():
                    process = queue.dequeue()
                    process.remaining_time_slice = self.time_quantum[i]
                    execution_time = min(process.remaining_time_slice, process.burst_time)
                    current_time += execution_time
                    process.burst_time -= execution_time

                    if process.burst_time > 0:
                        self.queue_service.demote_process(process, current_time, i)

                    self.queue_service.print_queues(current_time)
                    self.visualizer.save_queue_image(self.queues, current_time)
                    self.root.after(500, lambda: None)
                    time.sleep(1)
                    processed = True
                    break
            if not processed:
                break

        self.visualizer.create_animation()