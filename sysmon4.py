import tkinter as tk
from tkinter import ttk
import psutil
import math
import threading
import time
from datetime import datetime, timedelta

class GamingRGBMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Gaming System Dashboard 🎮")
        self.root.geometry("1200x700")
        self.root.configure(bg='#0a0a0a')
        
        # Gaming RGB color scheme
        self.colors = {
            'bg': '#0a0a0a',
            'card_bg': '#1a1a1a',
            'border': '#00ff88',
            'accent': '#00ff88',
            'text': '#ffffff',
            'value_text': '#00ff88',
            'led_green': '#00ff00',
            'led_yellow': '#ffff00',
            'led_red': '#ff0000',
            'led_off': '#333333',
            'rgb_blue': '#0088ff',
            'rgb_purple': '#ff00ff',
            'rgb_cyan': '#00ffff'
        }
        
        # LED blink states
        self.led_blink_state = True
        self.blink_counter = 0
        self.start_time = time.time()
        
        # Monitoring data
        self.cpu_usage = 0
        self.memory_usage = 0
        self.disk_usage = 0
        self.network_upload = 0
        self.network_download = 0
        self.cpu_temp = 0
        self.fan_speed = 1200
        
        # Network data for calculating speeds
        self.prev_net_io = None
        self.network_samples = []
        
        self.monitoring = True
        
        self.create_gaming_ui()
        self.start_monitoring()
        self.start_led_blink()
    
    def create_gaming_ui(self):
        # Main container with gaming border
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with gaming style
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🎮 GAMING SYSTEM DASHBOARD 🎮", 
                              font=("Consolas", 20, "bold"), 
                              fg=self.colors['accent'], 
                              bg=self.colors['bg'])
        title_label.pack(pady=10)
        
        # Main dashboard grid
        dashboard_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top row - CPU, Memory, Disk
        top_row = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        top_row.pack(fill=tk.X, pady=(0, 20))
        
        # CPU Card
        cpu_card = self.create_gaming_card(top_row, "CPU", "85.5%")
        cpu_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Memory Card
        memory_card = self.create_gaming_card(top_row, "MEMORY", "72.3%")
        memory_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Disk Card
        disk_card = self.create_gaming_card(top_row, "DISK", "45.2%")
        disk_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Bottom row - Network and System Info
        bottom_row = tk.Frame(dashboard_frame, bg=self.colors['bg'])
        bottom_row.pack(fill=tk.BOTH, expand=True)
        
        # Network Card
        network_card = self.create_gaming_card(bottom_row, "NETWORK", "2.1 MB/s")
        network_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # System Info Card
        system_card = self.create_system_info_card(bottom_row)
        system_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Store canvas references for updates
        self.canvas_refs = {
            'cpu': self.cpu_canvas,
            'memory': self.memory_canvas,
            'disk': self.disk_canvas,
            'network': self.network_canvas
        }
        
        self.value_labels = {
            'cpu': self.cpu_value,
            'memory': self.memory_value,
            'disk': self.disk_value,
            'network': self.network_value
        }
        
        # System info labels
        self.system_labels = {
            'status': self.status_label,
            'temp': self.temp_label,
            'uptime': self.uptime_label,
            'fps': self.fps_label,
            'ping': self.ping_label
        }
    
    def create_gaming_card(self, parent, title, default_value):
        """Create a gaming-style card with LED bars and value display"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=2)
        card.config(highlightbackground=self.colors['border'], highlightthickness=2)
        
        # Title
        title_label = tk.Label(card, text=title, font=("Consolas", 14, "bold"),
                              fg=self.colors['accent'], bg=self.colors['card_bg'])
        title_label.pack(pady=10)
        
        # LED bars container
        led_frame = tk.Frame(card, bg=self.colors['card_bg'], height=120)
        led_frame.pack(fill=tk.X, padx=20, pady=10)
        led_frame.pack_propagate(False)
        
        # Create LED bars canvas
        canvas = tk.Canvas(led_frame, bg=self.colors['card_bg'], highlightthickness=0, height=120)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Value display
        value_frame = tk.Frame(card, bg=self.colors['card_bg'])
        value_frame.pack(pady=10)
        
        value_label = tk.Label(value_frame, text=default_value, font=("Consolas", 16, "bold"),
                              fg=self.colors['value_text'], bg=self.colors['card_bg'])
        value_label.pack()
        
        # Store references
        if title == "CPU":
            self.cpu_canvas = canvas
            self.cpu_value = value_label
        elif title == "MEMORY":
            self.memory_canvas = canvas
            self.memory_value = value_label
        elif title == "DISK":
            self.disk_canvas = canvas
            self.disk_value = value_label
        elif title == "NETWORK":
            self.network_canvas = canvas
            self.network_value = value_label
        
        return card
    
    def create_system_info_card(self, parent):
        """Create system information card"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=2)
        card.config(highlightbackground=self.colors['rgb_blue'], highlightthickness=2)
        
        # Title
        title_label = tk.Label(card, text="SYSTEM INFO", font=("Consolas", 14, "bold"),
                              fg=self.colors['rgb_blue'], bg=self.colors['card_bg'])
        title_label.pack(pady=10)
        
        # System info content
        info_frame = tk.Frame(card, bg=self.colors['card_bg'])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status
        status_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        status_frame.pack(fill=tk.X, pady=5)
        tk.Label(status_frame, text="STATUS:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        self.status_label = tk.Label(status_frame, text="● OPTIMAL", font=("Consolas", 10, "bold"),
                                    fg=self.colors['led_green'], bg=self.colors['card_bg'])
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Temperature
        temp_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        temp_frame.pack(fill=tk.X, pady=5)
        tk.Label(temp_frame, text="TEMP:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        self.temp_label = tk.Label(temp_frame, text="45°C", font=("Consolas", 10),
                                  fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.temp_label.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(temp_frame, text="| FAN:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT, padx=(20, 0))
        self.fan_label = tk.Label(temp_frame, text="1200 RPM", font=("Consolas", 10),
                                 fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.fan_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Uptime
        uptime_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        uptime_frame.pack(fill=tk.X, pady=5)
        tk.Label(uptime_frame, text="UPTIME:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        self.uptime_label = tk.Label(uptime_frame, text="0:00:00", font=("Consolas", 10),
                                    fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.uptime_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # FPS (simulated for gaming feel)
        fps_frame = tk.Frame(info_frame, bg=self.colors['card_bg'])
        fps_frame.pack(fill=tk.X, pady=5)
        tk.Label(fps_frame, text="FPS:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        self.fps_label = tk.Label(fps_frame, text="144", font=("Consolas", 10),
                                 fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.fps_label.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(fps_frame, text="| PING:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT, padx=(20, 0))
        self.ping_label = tk.Label(fps_frame, text="24ms", font=("Consolas", 10),
                                  fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.ping_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Additional system info
        info_frame2 = tk.Frame(info_frame, bg=self.colors['card_bg'])
        info_frame2.pack(fill=tk.X, pady=5)
        tk.Label(info_frame2, text="CPU FREQ:", font=("Consolas", 10, "bold"),
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(side=tk.LEFT)
        self.freq_label = tk.Label(info_frame2, text="3600 MHz", font=("Consolas", 10),
                                  fg=self.colors['value_text'], bg=self.colors['card_bg'])
        self.freq_label.pack(side=tk.LEFT, padx=(10, 0))
        
        return card
    
    def draw_led_bars(self, canvas, value, label):
        """Draw 20 LED bars based on usage value"""
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:  # Canvas not yet rendered
            width = 300
            height = 120
        
        # Adjust value for network (0-10 MB/s scale)
        if label == "NETWORK":
            max_net = 10
            adjusted_value = min(value / max_net * 100, 100)
        else:
            adjusted_value = value
        
        # LED dimensions
        num_leds = 20
        led_width = (width - 40) // num_leds
        led_height = 20
        led_spacing = 2
        start_x = 20
        
        # Calculate how many LEDs should be on
        leds_on = int((adjusted_value / 100) * num_leds)
        
        # Determine blink state for active LEDs
        blink_on = self.led_blink_state
        
        # Create 20 LED bars
        for i in range(num_leds):
            # Determine LED color based on position
            if i < 7:  # 0-6: Green (0-35%)
                base_color = self.colors['led_green']
            elif i < 14:  # 7-13: Yellow (35-70%)
                base_color = self.colors['led_yellow']
            else:  # 14-19: Red (70-100%)
                base_color = self.colors['led_red']
            
            # Determine if this LED should be on
            led_on = i < leds_on
            
            # Set LED color (on with blink or off)
            if led_on and blink_on:
                led_color = base_color
            else:
                led_color = self.colors['led_off']
            
            # Calculate position
            x1 = start_x + (i * (led_width + led_spacing))
            y1 = (height - led_height) // 2
            x2 = x1 + led_width
            y2 = y1 + led_height
            
            # Draw LED with 3D effect
            canvas.create_rectangle(x1, y1, x2, y2, fill=led_color, outline='#666666', width=1)
            
            # Add subtle gradient effect
            if led_on and blink_on:
                canvas.create_rectangle(x1, y1, x2, y1 + 3, fill='#ffffff', stipple='gray50', width=0)
    
    def start_led_blink(self):
        """Start LED blinking animation"""
        def blink():
            while self.monitoring:
                self.led_blink_state = not self.led_blink_state
                self.blink_counter += 1
                
                # Update all LED displays
                self.root.after(0, self.update_led_displays)
                
                time.sleep(0.3)  # Faster blink for gaming feel
        
        blink_thread = threading.Thread(target=blink, daemon=True)
        blink_thread.start()
    
    def update_led_displays(self):
        """Update all LED bar displays"""
        for label, canvas in self.canvas_refs.items():
            if label == 'cpu':
                value = self.cpu_usage
            elif label == 'memory':
                value = self.memory_usage
            elif label == 'disk':
                value = self.disk_usage
            elif label == 'network':
                value = self.network_upload
            
            self.draw_led_bars(canvas, value, label.upper())
    
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
    
    def get_cpu_temperature(self):
        """Try to get CPU temperature (works on some systems)"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif hasattr(psutil, "sensors_temperatures"):
                for name, entries in temps.items():
                    for entry in entries:
                        return entry.current
        except:
            pass
        return 45.0  # Fallback temperature
    
    def format_uptime(self):
        """Format uptime as HH:MM:SS"""
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def start_monitoring(self):
        def monitor():
            while self.monitoring:
                try:
                    # CPU usage
                    self.cpu_usage = psutil.cpu_percent(interval=0.5)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage = memory.percent
                    
                    # Disk usage
                    try:
                        disk = psutil.disk_usage('/')
                    except:
                        try:
                            disk = psutil.disk_usage('C:\\')
                        except:
                            disk = psutil.disk_usage('/')
                    self.disk_usage = (disk.used / disk.total) * 100
                    
                    # Network usage
                    upload_speed, download_speed = self.get_network_speed()
                    self.network_upload = upload_speed
                    self.network_download = download_speed
                    
                    # System temperature
                    self.cpu_temp = self.get_cpu_temperature()
                    
                    # Simulate fan speed variation based on temperature
                    self.fan_speed = 800 + int((self.cpu_temp - 40) * 50)
                    self.fan_speed = max(800, min(self.fan_speed, 2000))
                    
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
        # Update value displays
        self.value_labels['cpu'].config(text=f"{cpu:.1f}%")
        self.value_labels['memory'].config(text=f"{memory:.1f}%")
        self.value_labels['disk'].config(text=f"{disk:.1f}%")
        self.value_labels['network'].config(text=f"{network:.2f} MB/s")
        
        # Update LED displays
        self.update_led_displays()
        
        # Update system info
        # Status based on highest usage
        max_usage = max(cpu, memory, disk)
        if max_usage > 90:
            status = "● CRITICAL"
            status_color = self.colors['led_red']
        elif max_usage > 70:
            status = "● HIGH LOAD"
            status_color = self.colors['led_yellow']
        elif max_usage > 50:
            status = "● MODERATE"
            status_color = self.colors['led_yellow']
        else:
            status = "● OPTIMAL"
            status_color = self.colors['led_green']
        
        self.system_labels['status'].config(text=status, fg=status_color)
        self.system_labels['temp'].config(text=f"{self.cpu_temp:.1f}°C")
        self.fan_label.config(text=f"{self.fan_speed} RPM")
        self.system_labels['uptime'].config(text=self.format_uptime())
        
        # Simulated FPS and Ping (for gaming feel)
        fps = max(60, 144 - int(cpu / 2))
        ping = max(10, 50 - int((100 - cpu) / 4))
        self.system_labels['fps'].config(text=str(fps))
        self.system_labels['ping'].config(text=f"{ping}ms")
        
        # CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                self.freq_label.config(text=f"{freq.current:.0f} MHz")
        except:
            self.freq_label.config(text="N/A")
    
    def on_closing(self):
        self.monitoring = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GamingRGBMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()