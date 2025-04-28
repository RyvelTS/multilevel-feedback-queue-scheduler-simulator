# MLFQ Simulator

A Python-based simulator for the **Multi-Level Feedback Queue (MLFQ)** scheduling algorithm, commonly used in operating systems to manage process scheduling.

---

## Features

- Simulates the MLFQ scheduling algorithm.
- Visualizes scheduling behavior using **matplotlib**.
- Generates GIFs of scheduling processes using **imageio**.

---

## Installation

### 1. Activate Virtual Environment
Ensure you have a Python virtual environment activated:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install matplotlib imageio
```

---

## Usage

Run the simulator using the following command:
```bash
python -m mlfq-simulator.main
```
---

## Project Structure

```
📂 mlfq-simulator
├── main.py          # Entry point for the simulator
├── scheduler.py     # Core logic for MLFQ scheduling
├── visualizer.py    # Visualization and GIF generation
└── README.md        # Project documentation
```

---

## How It Works

The MLFQ simulator models a multi-level feedback queue scheduling system:
1. **Multiple Queues**: Processes are assigned to different priority levels.
2. **Dynamic Priority Adjustment**: Processes move between queues based on their behavior.
3. **Visualization**: The scheduling process is visualized step-by-step.

---

## Example Output

### Visualization
The simulator generates a graphical representation of process scheduling

### GIF Output
A GIF of the scheduling process is saved for further analysis
For detailed information, refer to the implementation in `visualizer_service.py`.

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the simulator.

---

## Author

**Ryvel Timothy**
UESTC, Spring 2025
Course: Operating Systems