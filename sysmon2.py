import tkinter as tk
from tkinter import ttk
import psutil
import math
import threading
import time

class SpeedometerMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Vintage System Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Colors for vintage look
        self.colors = {
            'bg': '#2b2b2b',
            'dial_bg': '#1a1a1a',
            'dial_face': '#3a3a3a',
            'needle': '#ff4444',
            'scale': '#e6e6e6',
            'text': '#e6e6e6',
            'accent': '#ffaa00',
            'glass': '#aaffff'
        }
        
        # Monitoring data
        self.cpu_usage = 0
        self.memory_usage = 0
        self.disk_usage = 0
        self.network_upload = 0
        self.network_download = 0
        
        # Network data for calculating speeds
        self.prev_net_io = None
        self.network_samples = []
        
        self.monitoring = True
        
        self.create_widgets()
        self.start_monitoring()
    
    def create_widgets(self):
        # Main container with vintage border
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], relief='raised', bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="VINTAGE SYSTEM MONITOR", 
                              font=("Courier", 20, "bold"), 
                              fg=self.colors['accent'], 
                              bg=self.colors['bg'])
        title_label.pack(pady=10)
        
        # Dashboard frame
        dashboard_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Top row - CPU and Memory
        top_frame = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, pady=10)
        
        # CPU Speedometer
        cpu_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        cpu_frame.pack(side=tk.LEFT, padx=20)
        self.cpu_canvas = tk.Canvas(cpu_frame, width=300, height=300, 
                                   bg=self.colors['bg'], highlightthickness=0)
        self.cpu_canvas.pack()
        tk.Label(cpu_frame, text="CPU USAGE", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=5)
        
        # Memory Speedometer
        memory_frame = tk.Frame(top_frame, bg=self.colors['bg'])
        memory_frame.pack(side=tk.RIGHT, padx=20)
        self.memory_canvas = tk.Canvas(memory_frame, width=300, height=300, 
                                      bg=self.colors['bg'], highlightthickness=0)
        self.memory_canvas.pack()
        tk.Label(memory_frame, text="MEMORY USAGE", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=5)
        
        # Bottom row - Disk and Network
        bottom_frame = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.X, pady=10)
        
        # Disk Speedometer
        disk_frame = tk.Frame(bottom_frame, bg=self.colors['bg'])
        disk_frame.pack(side=tk.LEFT, padx=20)
        self.disk_canvas = tk.Canvas(disk_frame, width=300, height=300, 
                                    bg=self.colors['bg'], highlightthickness=0)
        self.disk_canvas.pack()
        tk.Label(disk_frame, text="DISK USAGE", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=5)
        
        # Network Speedometer
        network_frame = tk.Frame(bottom_frame, bg=self.colors['bg'])
        network_frame.pack(side=tk.RIGHT, padx=20)
        self.network_canvas = tk.Canvas(network_frame, width=300, height=300, 
                                       bg=self.colors['bg'], highlightthickness=0)
        self.network_canvas.pack()
        tk.Label(network_frame, text="NETWORK UPLOAD", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=5)
        
        # Additional info frame
        info_frame = tk.Frame(main_frame, bg=self.colors['dial_bg'])
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # CPU info
        cpu_info = tk.Frame(info_frame, bg=self.colors['dial_bg'])
        cpu_info.pack(side=tk.LEFT, padx=20)
        tk.Label(cpu_info, text="CPU Info", font=("Arial", 10, "bold"), 
                fg=self.colors['accent'], bg=self.colors['dial_bg']).pack()
        self.cpu_freq_label = tk.Label(cpu_info, text="Freq: N/A", font=("Arial", 8), 
                                      fg=self.colors['text'], bg=self.colors['dial_bg'])
        self.cpu_freq_label.pack()
        
        # Memory info
        mem_info = tk.Frame(info_frame, bg=self.colors['dial_bg'])
        mem_info.pack(side=tk.LEFT, padx=20)
        tk.Label(mem_info, text="Memory Info", font=("Arial", 10, "bold"), 
                fg=self.colors['accent'], bg=self.colors['dial_bg']).pack()
        self.mem_details_label = tk.Label(mem_info, text="Used: N/A", font=("Arial", 8), 
                                         fg=self.colors['text'], bg=self.colors['dial_bg'])
        self.mem_details_label.pack()
        
        # Disk info
        disk_info = tk.Frame(info_frame, bg=self.colors['dial_bg'])
        disk_info.pack(side=tk.LEFT, padx=20)
        tk.Label(disk_info, text="Disk Info", font=("Arial", 10, "bold"), 
                fg=self.colors['accent'], bg=self.colors['dial_bg']).pack()
        self.disk_details_label = tk.Label(disk_info, text="Used: N/A", font=("Arial", 8), 
                                          fg=self.colors['text'], bg=self.colors['dial_bg'])
        self.disk_details_label.pack()
        
        # Network info
        net_info = tk.Frame(info_frame, bg=self.colors['dial_bg'])
        net_info.pack(side=tk.LEFT, padx=20)
        tk.Label(net_info, text="Network Info", font=("Arial", 10, "bold"), 
                fg=self.colors['accent'], bg=self.colors['dial_bg']).pack()
        self.net_details_label = tk.Label(net_info, text="Download: N/A", font=("Arial", 8), 
                                         fg=self.colors['text'], bg=self.colors['dial_bg'])
        self.net_details_label.pack()
        
        # Status bar at bottom
        status_frame = tk.Frame(main_frame, bg=self.colors['dial_bg'], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="SYSTEM STATUS: NORMAL", 
                                    font=("Courier", 10), 
                                    fg=self.colors['accent'], 
                                    bg=self.colors['dial_bg'])
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Draw initial speedometers
        self.draw_speedometer(self.cpu_canvas, "CPU", 0)
        self.draw_speedometer(self.memory_canvas, "MEM", 0)
        self.draw_speedometer(self.disk_canvas, "DISK", 0)
        self.draw_speedometer(self.network_canvas, "NET", 0)
    
    def draw_speedometer(self, canvas, label, value):
        canvas.delete("all")
        width = 300
        height = 300
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 20
        
        # Draw outer dial
        canvas.create_oval(center_x - radius, center_y - radius,
                          center_x + radius, center_y + radius,
                          outline=self.colors['scale'], width=3, fill=self.colors['dial_face'])
        
        # Draw inner dial (metal ring effect)
        inner_radius = radius - 15
        canvas.create_oval(center_x - inner_radius, center_y - inner_radius,
                          center_x + inner_radius, center_y + inner_radius,
                          outline=self.colors['accent'], width=2, fill=self.colors['dial_bg'])
        
        # Draw scale markings
        self.draw_scale_marks(canvas, center_x, center_y, radius, label)
        
        # Draw needle
        angle = self.value_to_angle(value, label)
        needle_length = radius - 30
        end_x = center_x + needle_length * math.sin(math.radians(angle))
        end_y = center_y - needle_length * math.cos(math.radians(angle))
        
        # Draw needle with pivot point
        canvas.create_line(center_x, center_y, end_x, end_y, 
                          fill=self.colors['needle'], width=3, arrow=tk.LAST, arrowshape=(8, 10, 5))
        canvas.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5,
                          fill=self.colors['needle'], outline=self.colors['accent'])
        
        # Draw value display
        display_radius = radius // 3
        canvas.create_oval(center_x - display_radius, center_y - display_radius,
                          center_x + display_radius, center_y + display_radius,
                          fill=self.colors['dial_bg'], outline=self.colors['accent'])
        
        value_text = f"{value:.1f}%"
        if label == "NET":  # Network shows MB/s
            value_text = f"{value:.2f}\nMB/s"
        
        canvas.create_text(center_x, center_y, text=value_text,
                          font=("Arial", 12, "bold"), fill=self.colors['text'])
        
        # Draw label
        canvas.create_text(center_x, center_y + radius - 20, text=label,
                          font=("Arial", 10, "bold"), fill=self.colors['accent'])
        
        # Draw glass reflection effect
        self.draw_glass_effect(canvas, center_x, center_y, radius)
    
    def draw_scale_marks(self, canvas, cx, cy, radius, label):
        max_value = 100
        if label == "NET":
            max_value = 10  # 10 MB/s max for network
            
        # Major marks
        major_divisions = 5
        for i in range(major_divisions + 1):
            value = (i / major_divisions) * max_value
            angle = self.value_to_angle(value, label)
            start_radius = radius - 10
            end_radius = radius - 20
            
            start_x = cx + start_radius * math.sin(math.radians(angle))
            start_y = cy - start_radius * math.cos(math.radians(angle))
            end_x = cx + end_radius * math.sin(math.radians(angle))
            end_y = cy - end_radius * math.cos(math.radians(angle))
            
            canvas.create_line(start_x, start_y, end_x, end_y, 
                              fill=self.colors['scale'], width=2)
            
            # Add numbers
            text_radius = radius - 35
            text_x = cx + text_radius * math.sin(math.radians(angle))
            text_y = cy - text_radius * math.cos(math.radians(angle))
            
            canvas.create_text(text_x, text_y, text=str(int(value)),
                              font=("Arial", 8, "bold"), fill=self.colors['text'])
        
        # Minor marks
        minor_divisions = max_value
        for i in range(minor_divisions + 1):
            if i % (max_value // major_divisions) == 0:
                continue
            value = i
            angle = self.value_to_angle(value, label)
            start_radius = radius - 10
            end_radius = radius - 15
            
            start_x = cx + start_radius * math.sin(math.radians(angle))
            start_y = cy - start_radius * math.cos(math.radians(angle))
            end_x = cx + end_radius * math.sin(math.radians(angle))
            end_y = cy - end_radius * math.cos(math.radians(angle))
            
            canvas.create_line(start_x, start_y, end_x, end_y, 
                              fill=self.colors['scale'], width=1)
    
    def draw_glass_effect(self, canvas, cx, cy, radius):
        for i in range(5):
            y_offset = cy - radius + 10 + i * 5
            canvas.create_line(cx - radius + 10, y_offset, 
                              cx + radius - 10, y_offset,
                              fill=self.colors['glass'], width=1)
    
    def value_to_angle(self, value, label):
        if label == "NET":  # Network uses different scale
            max_net = 10  # 10 MB/s max scale
            scaled_value = min(value / max_net * 100, 100)
        else:
            scaled_value = value
        
        return 135 + (scaled_value * 2.7)  # 135° to 405° = 270° sweep
    
    def get_network_speed(self):
        """Get current network upload/download speed in MB/s"""
        current_net_io = psutil.net_io_counters()
        
        if self.prev_net_io is None:
            self.prev_net_io = current_net_io
            return 0, 0
        
        # Calculate speeds in MB/s
        time_diff = 1  # 1 second interval
        upload_speed = (current_net_io.bytes_sent - self.prev_net_io.bytes_sent) / (1024 * 1024) / time_diff
        download_speed = (current_net_io.bytes_recv - self.prev_net_io.bytes_recv) / (1024 * 1024) / time_diff
        
        self.prev_net_io = current_net_io
        
        # Smooth the network speed (average last 3 samples)
        self.network_samples.append(upload_speed)
        if len(self.network_samples) > 3:
            self.network_samples.pop(0)
        
        smoothed_upload = sum(self.network_samples) / len(self.network_samples)
        
        return smoothed_upload, download_speed
    
    def format_bytes(self, bytes_size):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    def start_monitoring(self):
        def monitor():
            while self.monitoring:
                try:
                    # CPU usage
                    self.cpu_usage = psutil.cpu_percent(interval=0.5)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage = memory.percent
                    
                    # Disk usage - try different partitions if root fails
                    try:
                        disk = psutil.disk_usage('/')
                    except:
                        # Try C: drive on Windows or other common partitions
                        try:
                            disk = psutil.disk_usage('C:\\')
                        except:
                            disk = psutil.disk_usage('/')
                    self.disk_usage = (disk.used / disk.total) * 100
                    
                    # Network usage
                    upload_speed, download_speed = self.get_network_speed()
                    self.network_upload = upload_speed
                    self.network_download = download_speed
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_display, 
                                  self.cpu_usage, self.memory_usage, 
                                  self.disk_usage, upload_speed,
                                  memory, disk, download_speed)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                
                time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def update_display(self, cpu, memory, disk, network, memory_obj, disk_obj, download_speed):
        # Update speedometers
        self.draw_speedometer(self.cpu_canvas, "CPU", cpu)
        self.draw_speedometer(self.memory_canvas, "MEM", memory)
        self.draw_speedometer(self.disk_canvas, "DISK", disk)
        self.draw_speedometer(self.network_canvas, "NET", network)
        
        # Update detailed information
        # CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                self.cpu_freq_label.config(text=f"Freq: {freq.current:.0f} MHz")
        except:
            self.cpu_freq_label.config(text="Freq: N/A")
        
        # Memory details
        mem_used = self.format_bytes(memory_obj.used)
        mem_total = self.format_bytes(memory_obj.total)
        self.mem_details_label.config(text=f"Used: {mem_used} / {mem_total}")
        
        # Disk details
        disk_used = self.format_bytes(disk_obj.used)
        disk_total = self.format_bytes(disk_obj.total)
        self.disk_details_label.config(text=f"Used: {disk_used} / {disk_total}")
        
        # Network details
        self.net_details_label.config(text=f"Down: {download_speed:.2f} MB/s")
        
        # Update status based on highest usage
        max_usage = max(cpu, memory, disk)
        if max_usage > 90:
            status = "CRITICAL"
            color = "#ff0000"
        elif max_usage > 70:
            status = "HIGH LOAD"
            color = "#ffaa00"
        elif max_usage > 50:
            status = "MODERATE"
            color = "#ffff00"
        else:
            status = "NORMAL"
            color = "#00ff00"
        
        self.status_label.config(text=f"SYSTEM STATUS: {status}", fg=color)
    
    def on_closing(self):
        self.monitoring = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedometerMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()