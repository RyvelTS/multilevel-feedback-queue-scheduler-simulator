import imageio.v2 as imageio
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for image generation
import matplotlib.pyplot as plt
import numpy as np
import os, glob

class VisualizerService:
    def __init__(self, canvas, figure, gantt_canvas, gantt_figure):
        self.canvas = canvas
        self.figure = figure
        self.gantt_canvas = gantt_canvas
        self.gantt_figure = gantt_figure
        self.process_colors = {}
        self.frame_count = 0  # Initialize frame counter [[1]]
        self.output_dir = "result"
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory [[3]]
        self.cleanup_old_frames()
        self.max_burst_time = 0  # Track maximum burst time for x-axis locking
        self.gantt_events = []  # Store (process_id, start_time, end_time, queue_priority)

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
            ax.set_title(f'Queue {queue.priority + 1} ({priority_labels[queue.priority]})')
            ax.set_xlim(0, self.max_burst_time)  # Lock x-axis to max_burst_time

        self.figure.suptitle(f'MLFQ Scheduling - Time {current_time}')
        self.figure.tight_layout()
        self.canvas.draw()  # Update the Tkinter canvas

        # Save frame to file [[3]]
        frame_path = os.path.join(self.output_dir, f'frame_{self.frame_count}.png')
        self.figure.savefig(frame_path)
        self.frame_count += 1  # Increment counter

    def create_animation(self):
        """Generate GIF from saved frames and Gantt chart GIF from saved Gantt frames"""
        # Create queue animation
        images = []
        for i in range(self.frame_count):
            frame_path = os.path.join(self.output_dir, f'frame_{i}.png')
            if os.path.exists(frame_path):
                images.append(imageio.imread(frame_path))
        animation_path = os.path.join(self.output_dir, 'mlfq_animation.gif')
        imageio.mimsave(animation_path, images, fps=1)
        print(f"Animation saved to {animation_path}")

        # Create Gantt chart animation from saved frames
        gantt_frame_files = sorted(
            glob.glob(os.path.join(self.output_dir, 'gantt_frame_*.png')),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1])
        )
        gantt_images = [imageio.imread(f) for f in gantt_frame_files]
        gantt_gif_path = os.path.join(self.output_dir, 'mlfq_gantt_chart.gif')
        if gantt_images:
            imageio.mimsave(gantt_gif_path, gantt_images, fps=1)
            print(f"Gantt chart GIF saved to {gantt_gif_path}")
        else:
            print("No Gantt chart frames found to create GIF.")

    def cleanup_old_frames(self):
        """Delete existing frame files safely, including Gantt chart frames"""
        # Remove queue frames
        for filename in glob.glob(os.path.join(self.output_dir, 'frame_*.png')):
            try:
                os.remove(filename)
            except PermissionError:
                print(f"Warning: Could not delete {filename} - file in use")
        # Remove Gantt chart frames
        for filename in glob.glob(os.path.join(self.output_dir, 'gantt_frame_*.png')):
            try:
                os.remove(filename)
            except PermissionError:
                print(f"Warning: Could not delete {filename} - file in use")

    def record_gantt_event(self, process_id, start_time, end_time, queue_priority):
        """
        Call this method from the scheduler each time a process runs on CPU.
        """
        self.gantt_events.append((process_id, start_time, end_time, queue_priority))
        # Generate Gantt chart frames
        self.generate_gantt_chart()


    def generate_gantt_chart(self):
        """
        Generate and save Gantt chart frames from the recorded events.
        """
        if not self.gantt_events:
            print("No Gantt events to plot.")
            return

        color_map = self.process_colors if self.process_colors else {}

        max_time = max((end for _, _, end, _ in self.gantt_events), default=0)
        for upto in range(1, len(self.gantt_events) + 1):
            self.gantt_figure.clear() # Clear previous plot
            ax = self.gantt_figure.add_subplot(1, 1, 1)
            for idx, (pid, start, end, priority) in enumerate(self.gantt_events[:upto]):
                color = color_map.get(pid, '#CCCCCC')  # Use process color, fallback to gray
                ax.barh(0, end - start, left=start, height=0.5, color=color, edgecolor='black')
                ax.text((start + end) / 2, 0, f'P{pid}', va='center', ha='center', color='black', fontsize=8)
            ax.set_yticks([])
            ax.set_xlabel('Time')
            ax.set_title('Gantt Chart')
            ax.set_xlim(left=0, right=max_time)
            self.gantt_figure.tight_layout()
            # Save each frame as a permanent PNG
            frame_png_path = os.path.join(self.output_dir, f'gantt_frame_{upto}.png')
            self.gantt_figure.savefig(frame_png_path)
            self.gantt_canvas.draw()
