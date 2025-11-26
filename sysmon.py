import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Data storage for plotting
        self.cpu_data = [0] * 60
        self.memory_data = [0] * 60
        self.time_points = list(range(-59, 1))
        
        # Create the main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # CPU Tab
        self.cpu_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cpu_tab, text="CPU")
        
        # Memory Tab
        self.memory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_tab, text="Memory")
        
        # Setup CPU tab
        self.setup_cpu_tab()
        
        # Setup Memory tab
        self.setup_memory_tab()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.update_data)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def setup_cpu_tab(self):
        # CPU Usage Label
        self.cpu_label = tk.Label(self.cpu_tab, text="CPU Usage: 0%", font=("Arial", 16), fg="white", bg="#1e1e1e")
        self.cpu_label.pack(pady=10)
        
        # CPU Progress Bar
        self.cpu_progress = ttk.Progressbar(self.cpu_tab, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.cpu_progress.pack(pady=10)
        
        # CPU Details Frame
        details_frame = tk.Frame(self.cpu_tab, bg="#1e1e1e")
        details_frame.pack(pady=10, fill=tk.X)
        
        # CPU Cores
        self.core_labels = []
        cores_frame = tk.Frame(details_frame, bg="#1e1e1e")
        cores_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(cores_frame, text="CPU Cores", font=("Arial", 12, "bold"), fg="white", bg="#1e1e1e").pack()
        
        for i in range(psutil.cpu_count()):
            core_frame = tk.Frame(cores_frame, bg="#1e1e1e")
            core_frame.pack(fill=tk.X, pady=2)
            
            label = tk.Label(core_frame, text=f"Core {i}: 0%", font=("Arial", 10), fg="white", bg="#1e1e1e", width=12, anchor="w")
            label.pack(side=tk.LEFT)
            
            progress = ttk.Progressbar(core_frame, orient=tk.HORIZONTAL, length=150, mode='determinate')
            progress.pack(side=tk.LEFT, padx=5)
            
            self.core_labels.append((label, progress))
        
        # CPU Info
        info_frame = tk.Frame(details_frame, bg="#1e1e1e")
        info_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(info_frame, text="CPU Information", font=("Arial", 12, "bold"), fg="white", bg="#1e1e1e").pack()
        
        self.cpu_freq_label = tk.Label(info_frame, text="Frequency: N/A", font=("Arial", 10), fg="white", bg="#1e1e1e", anchor="w")
        self.cpu_freq_label.pack(fill=tk.X)
        
        self.cpu_count_label = tk.Label(info_frame, text=f"Cores: {psutil.cpu_count()}", font=("Arial", 10), fg="white", bg="#1e1e1e", anchor="w")
        self.cpu_count_label.pack(fill=tk.X)
        
        # CPU Usage Graph
        self.cpu_fig = Figure(figsize=(6, 3), dpi=100, facecolor='#1e1e1e')
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_facecolor('#1e1e1e')
        self.cpu_ax.tick_params(colors='white')
        self.cpu_ax.set_ylabel('CPU Usage (%)', color='white')
        self.cpu_ax.set_xlabel('Time (s)', color='white')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlim(-60, 0)
        self.cpu_line, = self.cpu_ax.plot(self.time_points, self.cpu_data, 'r-', linewidth=2)
        
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, self.cpu_tab)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_memory_tab(self):
        # Memory Usage Label
        self.memory_label = tk.Label(self.memory_tab, text="Memory Usage: 0%", font=("Arial", 16), fg="white", bg="#1e1e1e")
        self.memory_label.pack(pady=10)
        
        # Memory Progress Bar
        self.memory_progress = ttk.Progressbar(self.memory_tab, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.memory_progress.pack(pady=10)
        
        # Memory Details Frame
        memory_details_frame = tk.Frame(self.memory_tab, bg="#1e1e1e")
        memory_details_frame.pack(pady=10, fill=tk.X)
        
        # Memory Info
        memory_info_frame = tk.Frame(memory_details_frame, bg="#1e1e1e")
        memory_info_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(memory_info_frame, text="Memory Information", font=("Arial", 12, "bold"), fg="white", bg="#1e1e1e").pack()
        
        self.memory_total_label = tk.Label(memory_info_frame, text="Total: N/A", font=("Arial", 10), fg="white", bg="#1e1e1e", anchor="w")
        self.memory_total_label.pack(fill=tk.X)
        
        self.memory_used_label = tk.Label(memory_info_frame, text="Used: N/A", font=("Arial", 10), fg="white", bg="#1e1e1e", anchor="w")
        self.memory_used_label.pack(fill=tk.X)
        
        self.memory_available_label = tk.Label(memory_info_frame, text="Available: N/A", font=("Arial", 10), fg="white", bg="#1e1e1e", anchor="w")
        self.memory_available_label.pack(fill=tk.X)
        
        # Memory Usage Graph
        self.memory_fig = Figure(figsize=(6, 3), dpi=100, facecolor='#1e1e1e')
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_ax.set_facecolor('#1e1e1e')
        self.memory_ax.tick_params(colors='white')
        self.memory_ax.set_ylabel('Memory Usage (%)', color='white')
        self.memory_ax.set_xlabel('Time (s)', color='white')
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.set_xlim(-60, 0)
        self.memory_line, = self.memory_ax.plot(self.time_points, self.memory_data, 'g-', linewidth=2)
        
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, self.memory_tab)
        self.memory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_data(self):
        while self.monitoring:
            # Update CPU data
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_data.append(cpu_percent)
            if len(self.cpu_data) > 60:
                self.cpu_data.pop(0)
            
            # Update Memory data
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_data.append(memory_percent)
            if len(self.memory_data) > 60:
                self.memory_data.pop(0)
            
            # Update UI in main thread
            self.root.after(0, self.update_ui, cpu_percent, memory)
            
            time.sleep(1)
    
    def update_ui(self, cpu_percent, memory):
        # Update CPU UI
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_progress['value'] = cpu_percent
        
        # Update CPU cores
        cpu_percents = psutil.cpu_percent(percpu=True)
        for i, (label, progress) in enumerate(self.core_labels):
            if i < len(cpu_percents):
                label.config(text=f"Core {i}: {cpu_percents[i]:.1f}%")
                progress['value'] = cpu_percents[i]
        
        # Update CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                self.cpu_freq_label.config(text=f"Frequency: {freq.current:.0f} MHz")
        except:
            pass
        
        # Update Memory UI
        memory_percent = memory.percent
        self.memory_label.config(text=f"Memory Usage: {memory_percent:.1f}%")
        self.memory_progress['value'] = memory_percent
        
        # Format memory sizes
        def format_bytes(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} PB"
        
        self.memory_total_label.config(text=f"Total: {format_bytes(memory.total)}")
        self.memory_used_label.config(text=f"Used: {format_bytes(memory.used)}")
        self.memory_available_label.config(text=f"Available: {format_bytes(memory.available)}")
        
        # Update graphs
        self.update_graphs()
    
    def update_graphs(self):
        # Update CPU graph
        self.cpu_line.set_data(self.time_points, self.cpu_data)
        self.cpu_ax.relim()
        self.cpu_ax.autoscale_view()
        self.cpu_canvas.draw_idle()
        
        # Update Memory graph
        self.memory_line.set_data(self.time_points, self.memory_data)
        self.memory_ax.relim()
        self.memory_ax.autoscale_view()
        self.memory_canvas.draw_idle()
    
    def on_closing(self):
        self.monitoring = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()