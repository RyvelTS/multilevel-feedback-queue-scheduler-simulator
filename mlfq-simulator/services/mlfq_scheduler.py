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

        running_process = None
        running_queue_idx = None
        gantt_start_time = None  # Track when the current process started running

        while any(not q.is_empty() for q in self.queues) or running_process:
            # Promote processes that have waited too long
            self.queue_service.promote_processes(current_time, self.promotion_threshold)

            # If no process is running, pick the next one
            if not running_process:
                for i, queue in enumerate(self.queues):
                    if not queue.is_empty():
                        running_process = queue.dequeue()
                        running_queue_idx = i
                        running_process.remaining_time_slice = self.time_quantum[i]
                        gantt_start_time = current_time  # Mark start time for Gantt
                        break

            # If a process is running, execute it for one time unit
            if running_process:
                running_process.burst_time -= 1
                running_process.remaining_time_slice -= 1
                # Reset waiting time since it's now running
                running_process.entry_time = current_time + 1

                # --- Show running process in its queue for visualization ---
                if running_process.burst_time > 0:
                    self.queues[running_queue_idx].processes.insert(0, running_process)
                    self.queue_service.print_queues(current_time + 1)
                    self.visualizer.save_queue_image(self.queues, current_time + 1)
                    self.queues[running_queue_idx].processes.pop(0)
                else:
                    # If finished, do not show in queue
                    self.queue_service.print_queues(current_time + 1)
                    self.visualizer.save_queue_image(self.queues, current_time + 1)
                # ---------------------------------------------------------

                self.root.after(500, lambda: None)
                # Handle demotion or finishing after tick
                if running_process.burst_time == 0:
                    # Record Gantt event for finishing process
                    self.visualizer.record_gantt_event(
                        running_process.process_id,
                        gantt_start_time,
                        current_time + 1,
                        running_queue_idx
                    )
                    running_process = None
                    running_queue_idx = None
                    gantt_start_time = None
                elif running_process.remaining_time_slice == 0:
                    # Record Gantt event for time slice expiration
                    self.visualizer.record_gantt_event(
                        running_process.process_id,
                        gantt_start_time,
                        current_time + 1,
                        running_queue_idx
                    )
                    self.queue_service.demote_process(running_process, current_time + 1, running_queue_idx)
                    running_process = None
                    running_queue_idx = None
                    gantt_start_time = None

                current_time += 1
                time.sleep(0.5)
            else:
                break

        self.visualizer.create_animation()