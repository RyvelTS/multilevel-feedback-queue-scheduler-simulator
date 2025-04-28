import threading
from ..views import Menu
from ..models import Process
from ..services.mlfq_scheduler import MLFQ
from ..services.visualizer_service import VisualizerService

class App:
    """
    MLFQApp acts as the controller. It receives user input (via Menu),
    maintains the list of processes, and initiates the scheduling service.
    """
    def __init__(self, root):
        self.root = root
        self.setup_ui = Menu(root, self)
        self.visualizer = None  # Will be initialized later
        self.original_processes = []
        self.processes = []
        self.time_quantum = [2, 4, 8]
        self.promotion_threshold = 8

    def add_process(self, process_id, burst_time):
        new_process = Process(process_id, burst_time)
        self.original_processes.append(new_process)  # Store original
        self.processes.append(new_process)           # Working copy
        return True

    def update_process(self, process_id, burst_time=None):
        for process in self.processes:
            if process.process_id == process_id:
                if burst_time is not None:
                    process.burst_time = burst_time
                return True
        return False

    def remove_process(self, process_id):
        self.original_processes = [process for process in self.original_processes if process.process_id != process_id]
        self.processes = [process for process in self.processes if process.process_id != process_id]
        return True

    def start_simulation(self):
        # Reset processes from original definitions
        self.processes = [Process(p.process_id, p.burst_time)
                         for p in self.original_processes]

        def run_scheduler():
            self.visualizer = VisualizerService(
                canvas=self.setup_ui.canvas,
                figure=self.setup_ui.figure,
                gantt_canvas=self.setup_ui.gantt_canvas,
                gantt_figure=self.setup_ui.gantt_figure
            )
            scheduler_service = MLFQ(
                root=self.root,
                processes=self.processes.copy(),
                time_quantum=self.time_quantum,
                promotion_threshold=self.promotion_threshold,
                visualizer=self.visualizer
            )
            scheduler_service.run()
        threading.Thread(target=run_scheduler).start()
