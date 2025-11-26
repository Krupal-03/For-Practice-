import tkinter as tk
import psutil
import math
import threading
import time
import logging
from collections import deque
from tkinter import ttk

# Configuration constants
class Config:
    UPDATE_INTERVAL = 1000
    WINDOW_SIZE = "1000x700"
    HISTORY_SIZE = 60
    
    COLORS = {
        'cpu': '#ff6b6b',
        'ram': '#4ecdc4',
        'frequency': '#ff9ff3',
        'disk': '#96ceb4',
        'temp': '#feca57',
        'accent': '#ff6b6b',
        'bg': '#1e1e1e',
        'text': 'white'
    }
    
    COLOR_SCHEMES = {
        'dark': {'bg': '#1e1e1e', 'text': 'white', 'accent': '#ff6b6b'},
        'blue': {'bg': '#2c3e50', 'text': '#ecf0f1', 'accent': '#3498db'},
        'green': {'bg': '#1a2f1a', 'text': '#e8f5e8', 'accent': '#4CAF50'}
    }
    
    THRESHOLDS = {
        'cpu_warning': 80,
        'cpu_critical': 90,
        'temp_warning': 70,
        'temp_critical': 85
    }

# Metrics Collector Class
class MetricsCollector:
    def __init__(self):
        self.cpu_history = deque([0] * Config.HISTORY_SIZE, maxlen=Config.HISTORY_SIZE)
        self.last_update = 0
        self.cached_metrics = {}
        
    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            return temps['coretemp'][0].current if 'coretemp' in temps else 0
        except:
            return 0
    
    def get_cached_metrics(self):
        current_time = time.time()
        if current_time - self.last_update > 0.9:  # Cache for 0.9 seconds
            self.cached_metrics = self._get_metrics()
            self.last_update = current_time
        return self.cached_metrics
    
    def _get_metrics(self):
        cpu_percent = psutil.cpu_percent()
        self.cpu_history.append(cpu_percent)
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'ram_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'vram_percent': psutil.swap_memory().percent,
            'temperature': self.get_cpu_temperature(),
            'cpu_history': list(self.cpu_history)
        }

# Alert Manager Class
class AlertManager:
    def __init__(self):
        self.alerts_active = set()
        
    def check_thresholds(self, metrics):
        alerts = []
        
        if metrics['cpu_percent'] > Config.THRESHOLDS['cpu_critical']:
            alerts.append(("CRITICAL", f"CPU usage: {metrics['cpu_percent']:.1f}%"))
        elif metrics['cpu_percent'] > Config.THRESHOLDS['cpu_warning']:
            alerts.append(("WARNING", f"High CPU usage: {metrics['cpu_percent']:.1f}%"))
            
        if metrics['temperature'] > Config.THRESHOLDS['temp_critical']:
            alerts.append(("CRITICAL", f"CPU temperature: {metrics['temperature']:.1f}°C"))
        elif metrics['temperature'] > Config.THRESHOLDS['temp_warning']:
            alerts.append(("WARNING", f"High CPU temperature: {metrics['temperature']:.1f}°C"))
            
        return alerts

# Visualizer Class
class Visualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.glow_items = []
        
    def draw_circle_meter(self, x, y, radius, value, color, width=8):
        # Background circle
        bg_circle = self.canvas.create_arc(
            x - radius, y - radius, 
            x + radius, y + radius, 
            start=90, extent=359.9, outline='#333', width=width, style=tk.ARC
        )
        
        # Value circle
        value_circle = self.canvas.create_arc(
            x - radius, y - radius, 
            x + radius, y + radius, 
            start=90, extent=-3.6 * value, outline=color, width=width, style=tk.ARC
        )
        
        return bg_circle, value_circle
    
    def update_circle(self, item_id, value):
        self.canvas.itemconfig(item_id, extent=-3.6 * value)
    
    def add_glow_effect(self, item_id, color):
        # Simple glow effect by creating a slightly larger semi-transparent copy
        coords = self.canvas.coords(item_id)
        if coords:
            glow = self.canvas.create_arc(
                coords[0]-2, coords[1]-2, coords[2]+2, coords[3]+2,
                start=90, extent=self.canvas.itemcget(item_id, 'extent'),
                outline=color, width=2, style=tk.ARC
            )
            self.glow_items.append(glow)
            return glow

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.configure(bg=Config.COLORS['bg'])
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.logger = self.setup_logging()
        
        # Window setup
        self.root.geometry(Config.WINDOW_SIZE)
        self.center_window(1000, 700)
        self.root.minsize(800, 600)
        
        # Theme and state
        self.current_theme = 'dark'
        self.last_width = 0
        self.last_height = 0
        self.animation_step = 0
        
        # Create UI
        self.create_ui()
        self.setup_bindings()
        
        # Start monitoring
        self.start_monitoring()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('system_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('SystemMonitor')

    def create_ui(self):
        # Main canvas
        self.canvas = tk.Canvas(self.root, bg=Config.COLORS['bg'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        ttk.Button(control_frame, text="Theme", command=self.toggle_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export", command=self.export_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Task Manager", command=self.open_task_manager).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Quit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Initialize visualizer
        self.visualizer = Visualizer(self.canvas)
        
        # Create initial display
        self.create_display()

    def setup_bindings(self):
        self.root.bind('<Configure>', self.on_resize)
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F2>', lambda e: self.toggle_theme())

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_display(self):
        canvas_width = self.canvas.winfo_width() or 1000
        canvas_height = self.canvas.winfo_height() or 700
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Calculate sizes
        circle_radius = min(canvas_width, canvas_height) // 5
        bar_width = 20
        bar_height = min(400, canvas_height - 250)
        bar_spacing = min(300, canvas_width // 3)
        
        # System info at top
        self.info_text = self.canvas.create_text(
            center_x, 30, 
            text=f"CPU: {psutil.cpu_count()} Cores | RAM: {psutil.virtual_memory().total//(1024**3)}GB", 
            fill=Config.COLORS['text'], font=('Arial', 12), anchor='center'
        )
        
        # Left vertical bar - CPU Frequency
        left_bar_x = center_x - bar_spacing
        bar_bottom = 150 + bar_height
        
        self.canvas.create_text(left_bar_x, 100, text="CPU Frequency", 
                               fill=Config.COLORS['text'], font=('Arial', 10), anchor='center')
        
        self.left_bg = self.canvas.create_rectangle(
            left_bar_x - bar_width//2, 150, 
            left_bar_x + bar_width//2, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.left_fill = self.canvas.create_rectangle(
            left_bar_x - bar_width//2, bar_bottom, 
            left_bar_x + bar_width//2, bar_bottom, 
            fill=Config.COLORS['frequency']
        )
        self.left_text = self.canvas.create_text(
            left_bar_x, bar_bottom + 20, 
            text="0.0 GHz", fill=Config.COLORS['text'], font=('Arial', 9)
        )
        
        # Right vertical bar - CPU Usage
        right_bar_x = center_x + bar_spacing
        
        self.canvas.create_text(right_bar_x, 100, text="CPU Usage", 
                               fill=Config.COLORS['text'], font=('Arial', 10), anchor='center')
        
        self.right_bg = self.canvas.create_rectangle(
            right_bar_x - bar_width//2, 150, 
            right_bar_x + bar_width//2, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.right_fill = self.canvas.create_rectangle(
            right_bar_x - bar_width//2, bar_bottom, 
            right_bar_x + bar_width//2, bar_bottom, 
            fill=Config.COLORS['cpu']
        )
        self.right_text = self.canvas.create_text(
            right_bar_x, bar_bottom + 20, 
            text="0%", fill=Config.COLORS['text'], font=('Arial', 9)
        )
        
        # Large CPU pie chart in center
        self.cpu_bg, self.cpu_circle = self.visualizer.draw_circle_meter(
            center_x, center_y, circle_radius, 0, Config.COLORS['cpu']
        )
        
        self.cpu_text = self.canvas.create_text(
            center_x, center_y - 20, 
            text="CPU: 0%", fill=Config.COLORS['text'], font=('Arial', 16, 'bold')
        )
        self.cpu_freq_text = self.canvas.create_text(
            center_x, center_y + 15, 
            text="0.0 GHz", fill=Config.COLORS['frequency'], font=('Arial', 12)
        )
        
        # FPS counter
        self.fps_text = self.canvas.create_text(
            canvas_width - 50, 20, 
            text="FPS: 0", fill=Config.COLORS['text'], font=('Arial', 8), anchor='ne'
        )

    def start_monitoring(self):
        self.monitoring_thread = threading.Thread(target=self.update_metrics_threaded, daemon=True)
        self.monitoring_thread.start()

    def update_metrics_threaded(self):
        while True:
            self.update_metrics()
            time.sleep(Config.UPDATE_INTERVAL / 1000)

    def update_metrics(self):
        try:
            metrics = self.metrics_collector.get_cached_metrics()
            
            # Update window title with stats
            self.root.title(f"System Monitor - CPU: {metrics['cpu_percent']:.1f}%")
            
            # Update FPS counter (simplified)
            self.canvas.itemconfig(self.fps_text, text=f"FPS: {1}")
            
            # Update visual elements
            self.update_visuals(metrics)
            
            # Check alerts
            alerts = self.alert_manager.check_thresholds(metrics)
            if alerts:
                self.handle_alerts(alerts)
                
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def update_visuals(self, metrics):
        # Update large CPU pie chart
        self.visualizer.update_circle(self.cpu_circle, metrics['cpu_percent'])
        self.canvas.itemconfig(self.cpu_text, text=f"CPU: {metrics['cpu_percent']:.1f}%")
        self.canvas.itemconfig(self.cpu_freq_text, text=f"{metrics['cpu_freq']/1000:.1f} GHz")
        
        # Update vertical bars
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 50 and canvas_height > 50:
            center_x = canvas_width // 2
            bar_height = min(400, canvas_height - 250)
            bar_spacing = min(300, canvas_width // 3)
            bar_bottom = 150 + bar_height
            
            left_bar_x = center_x - bar_spacing
            right_bar_x = center_x + bar_spacing
            
            # Left vertical - CPU Frequency
            freq_height = (metrics['cpu_freq'] / self.metrics_collector.cached_metrics.get('max_freq', 4000)) * bar_height
            self.canvas.coords(
                self.left_fill, 
                left_bar_x - 10, bar_bottom - freq_height, 
                left_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.left_text, text=f"{metrics['cpu_freq']/1000:.1f} GHz")
            
            # Right vertical - CPU Usage
            usage_height = (metrics['cpu_percent'] / 100) * bar_height
            self.canvas.coords(
                self.right_fill, 
                right_bar_x - 10, bar_bottom - usage_height, 
                right_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.right_text, text=f"{metrics['cpu_percent']:.1f}%")

    def handle_alerts(self, alerts):
        for level, message in alerts:
            self.logger.warning(f"{level}: {message}")
            # In a full implementation, you could show visual alerts here

    def on_resize(self, event):
        if event.widget == self.root:
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            if (abs(current_width - self.last_width) > 50 or 
                abs(current_height - self.last_height) > 50):
                self.last_width = current_width
                self.last_height = current_height
                self.root.after(100, self.reposition_widgets)

    def reposition_widgets(self):
        self.canvas.delete("all")
        self.create_display()

    def toggle_theme(self):
        themes = list(Config.COLOR_SCHEMES.keys())
        current_index = themes.index(self.current_theme)
        next_theme = themes[(current_index + 1) % len(themes)]
        self.apply_theme(next_theme)

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = Config.COLOR_SCHEMES[theme_name]
        self.root.configure(bg=theme['bg'])
        self.canvas.configure(bg=theme['bg'])
        self.reposition_widgets()

    def export_stats(self):
        try:
            metrics = self.metrics_collector.get_cached_metrics()
            filename = f"system_stats_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"System Monitor Export - {time.ctime()}\n")
                f.write(f"CPU Usage: {metrics['cpu_percent']:.1f}%\n")
                f.write(f"CPU Frequency: {metrics['cpu_freq']/1000:.1f} GHz\n")
                f.write(f"RAM Usage: {metrics['ram_percent']:.1f}%\n")
                f.write(f"Disk Usage: {metrics['disk_percent']:.1f}%\n")
                f.write(f"Temperature: {metrics['temperature']:.1f}°C\n")
            self.logger.info(f"Stats exported to {filename}")
        except Exception as e:
            self.logger.error(f"Export failed: {e}")

    def open_task_manager(self):
        import os
        try:
            if os.name == 'nt':  # Windows
                os.system('taskmgr')
            else:  # Linux/Mac
                os.system('top')
        except Exception as e:
            self.logger.error(f"Failed to open task manager: {e}")

    def show_help(self):
        help_text = """
System Monitor Help:
- F1: Show this help
- F2: Toggle theme
- ESC: Exit fullscreen
- Resize: Auto-adjust layout
        """
        self.logger.info(help_text)

    # Property accessors for computed values
    @property
    def cpu_usage_percent(self):
        return self.metrics_collector.get_cached_metrics().get('cpu_percent', 0)

    @property
    def memory_usage_percent(self):
        return self.metrics_collector.get_cached_metrics().get('ram_percent', 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()