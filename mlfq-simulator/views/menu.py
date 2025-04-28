import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Menu:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("MLFQ Scheduler GUI")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)     # Minimum size restriction
        self.controller = controller
        self.process_id_counter = 1
        self.process_blocks = {}
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Right panel (visualization)
        self.right_frame = ttk.Frame(self.main_frame, borderwidth=2, relief="sunken")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configure grid for right_frame
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Left panel (controls)
        self.left_frame = ttk.Frame(self.main_frame, borderwidth=2, relief="sunken")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(4, weight=1)

        # Process Input Section (Left panel)
        self.input_frame = ttk.Frame(self.left_frame)
        self.input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.input_frame, text="Burst Time:").grid(row=0, column=0, padx=5)
        self.burst_time_entry = ttk.Entry(self.input_frame)
        self.burst_time_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.add_button = ttk.Button(self.input_frame, text="Add Process",
                                    command=self.add_process_block)
        self.add_button.grid(row=0, column=2, padx=5)

        # Batch Input Section (Left panel)
        self.batch_frame = ttk.Frame(self.left_frame)
        self.batch_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.batch_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.batch_frame, text="Batch Input (CSV format: burst_time per line):").grid(
            row=0, column=0, padx=5, sticky="w")
        self.batch_text = tk.Text(self.batch_frame, height=5)
        self.batch_text.grid(row=1, column=0, padx=5, sticky="ew")
        self.batch_button = ttk.Button(self.batch_frame, text="Add Batch Processes",
                                      command=self.add_batch_processes)
        self.batch_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Process Container (Left panel)
        self.process_container = ttk.Frame(self.left_frame)
        self.process_container.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.process_container.grid_columnconfigure(0, weight=1)
        self.process_container.grid_columnconfigure(1, weight=2)
        self.process_container.grid_columnconfigure(2, weight=1)

        # Process container header
        ttk.Label(self.process_container, text="Process ID").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(self.process_container, text="Burst Time").grid(
            row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(self.process_container, text="Actions").grid(
            row=0, column=2, padx=5, pady=5, sticky="e")

        # Execution Section (Left panel)
        self.execution_frame = ttk.Frame(self.left_frame)
        self.execution_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.start_button = ttk.Button(self.execution_frame, text="Start Simulation",
                                      command=self.start_simulation)
        self.start_button.pack(fill=tk.X, expand=True)

    def add_process_block(self, burst_time=None):
        try:
            if burst_time is None:
                burst_time = int(self.burst_time_entry.get())
            process_id = self.process_id_counter
            self.process_id_counter += 1

            row = len(self.process_blocks) + 1
            ttk.Label(self.process_container, text=str(process_id)).grid(
                row=row, column=0, padx=5, pady=2, sticky="w")

            # Burst time entry
            burst_var = tk.IntVar(value=burst_time)
            burst_entry = ttk.Entry(self.process_container, textvariable=burst_var)
            burst_entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            burst_entry.bind("<FocusOut>", lambda e: self.update_burst_time(process_id, burst_var.get()))

            # Delete button
            delete_btn = ttk.Button(self.process_container, text="Delete",
                                   command=lambda id=process_id: self.delete_process(id))
            delete_btn.grid(row=row, column=2, padx=5, pady=2, sticky="e")

            # Store references
            self.process_blocks[process_id] = {
                'row': row,
                'widgets': [  # Keep track of all widgets in the row [[6]]
                    self.process_container.grid_slaves(row=row, column=0)[0],
                    burst_entry,
                    delete_btn
                ],
                'burst_var': burst_var
            }

            self.controller.add_process(process_id, burst_time)
            if 'burst_time_entry' in locals():
                self.burst_time_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Burst time must be an integer")

    def delete_process(self, process_id):
        if messagebox.askyesno("Confirm", f"Delete process {process_id}?"):
            # Remove from controller
            self.controller.remove_process(process_id)

            # Remove from GUI [[6]]
            for widget in self.process_blocks[process_id]['widgets']:
                widget.destroy()

            # Remove from tracking dictionary
            del self.process_blocks[process_id]

            # Re-number remaining rows [[7]]
            for idx, pid in enumerate(self.process_blocks.keys()):
                row = idx + 1  # Skip header row
                for col in range(3):
                    widget = self.process_blocks[pid]['widgets'][col]
                    widget.grid(row=row, column=col)

    def add_batch_processes(self):
        content = self.batch_text.get("1.0", tk.END).strip()
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                burst_time = int(line)
                self.add_process_block(burst_time)
            except ValueError:
                messagebox.showerror("Error", f"Invalid burst time: {line}")

        self.batch_text.delete("1.0", tk.END)

    def update_burst_time(self, process_id, new_time):
        try:
            new_time = int(new_time)
            self.controller.update_process(process_id, new_time)
        except ValueError:
            messagebox.showerror("Error", "Invalid burst time value")

    def start_simulation(self):
        self.controller.start_simulation()