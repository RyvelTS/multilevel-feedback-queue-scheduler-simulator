class QueueService:
    def __init__(self, queues):
        self.queues = queues

    def promote_processes(self, current_time, promotion_threshold):
        """Promote processes waiting too long from lower queues to a higher queue."""
        for i in range(1, len(self.queues)):
            queue = self.queues[i]
            for process in list(queue.processes):
                if current_time - process.entry_time >= promotion_threshold:
                    queue.processes.remove(process)
                    self.queues[i - 1].enqueue(process, current_time)

    def demote_process(self, process, current_time, current_queue_index):
        """Demote a process to the next lower-priority queue."""
        new_priority = min(current_queue_index + 1, len(self.queues) - 1)
        self.queues[new_priority].enqueue(process, current_time)

    def print_queues(self, current_time):
        print(f"\nTime: {current_time}")
        for queue in self.queues:
            priority_name = ["High", "Medium", "Low"][queue.priority] if queue.priority < 3 else f"Queue {queue.priority}"
            print(f"Queue {queue.priority} ({priority_name}):")
            for p in queue.processes:
                wt = current_time - p.entry_time
                rt = p.remaining_time_slice if p.remaining_time_slice is not None else "-"
                print(f"  Process P{p.process_id} | Remaining Burst: {p.burst_time} | Priority: {p.priority} | WT: {wt} | RT Slice: {rt}")