import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
import os, glob

class VisualizerService:
    def __init__(self, canvas, figure):
        self.canvas = canvas
        self.figure = figure
        self.process_colors = {}
        self.frame_count = 0  # Initialize frame counter [[1]]
        self.output_dir = "result"
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory [[3]]
        self.cleanup_old_frames()
        self.max_burst_time = 0  # Track maximum burst time for x-axis locking

    def assign_colors(self, processes):
        color_list = plt.cm.tab10.colors[:len(processes)]
        self.process_colors = {p.process_id: color_list[i] for i, p in enumerate(processes)}

    def save_queue_image(self, queues, current_time):
        self.figure.clear()  # Clear previous plot
        priority_labels = ["High", "Medium", "Low"]

        # Update max_burst_time based on the first frame
        if self.frame_count == 0:
            self.max_burst_time = max(
                (p.burst_time for queue in queues for p in queue.processes), default=0
            )

        for i, queue in enumerate(queues):
            ax = self.figure.add_subplot(len(queues), 1, i+1)
            y_positions = np.arange(len(queue.processes))
            burst_times = [p.burst_time for p in queue.processes]
            labels = [f'P{p.process_id}\nWT:{current_time - p.entry_time}'
                     for p in queue.processes]
            colors = [self.process_colors[p.process_id] for p in queue.processes]

            ax.barh(y_positions, burst_times, color=colors, edgecolor='black')
            ax.set_yticks(y_positions)
            ax.set_yticklabels(labels)
            ax.set_title(f'Queue {queue.priority} ({priority_labels[queue.priority]})')
            ax.set_xlim(0, self.max_burst_time)  # Lock x-axis to max_burst_time

        self.figure.suptitle(f'MLFQ Scheduling - Time {current_time}')
        self.figure.tight_layout()
        self.canvas.draw()  # Update the Tkinter canvas

        # Save frame to file [[3]]
        frame_path = os.path.join(self.output_dir, f'frame_{self.frame_count}.png')
        self.figure.savefig(frame_path)
        self.frame_count += 1  # Increment counter

    def create_animation(self):
        """Generate GIF from saved frames"""
        images = []
        for i in range(self.frame_count):
            frame_path = os.path.join(self.output_dir, f'frame_{i}.png')
            if os.path.exists(frame_path):
                images.append(imageio.imread(frame_path))
        animation_path = os.path.join(self.output_dir, 'mlfq_animation.gif')
        imageio.mimsave(animation_path, images, fps=1)
        print(f"Animation saved to {animation_path}")

    def cleanup_old_frames(self):
        """Delete existing frame files safely"""
        for filename in glob.glob(os.path.join(self.output_dir, 'frame_*.png')):
            try:
                os.remove(filename)
            except PermissionError:
                print(f"Warning: Could not delete {filename} - file in use")