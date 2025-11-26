import tkinter as tk
import psutil
import threading
import time
import logging
from collections import deque
from tkinter import ttk

# Configuration constants
class Config:
    UPDATE_INTERVAL = 1000
    WINDOW_SIZE = "1400x800"
    HISTORY_SIZE = 60
    
    COLORS = {
        'cpu': '#ff6b6b',
        'ram': '#4ecdc4',
        'gpu': '#45b7d1',
        'gpu_freq': '#ff9ff3',
        'fan': '#feca57',
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
        self.ram_history = deque([0] * Config.HISTORY_SIZE, maxlen=Config.HISTORY_SIZE)
        self.last_update = 0
        self.cached_metrics = {}
        
    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            return temps['coretemp'][0].current if 'coretemp' in temps else 0
        except:
            return 0
    
    def get_fan_speeds(self):
        """Get fan speeds - simulates multiple fans for demonstration"""
        try:
            # psutil doesn't have direct fan speed access, so we simulate it
            # In real implementation, you might use other libraries
            fans = []
            # Simulate 1-3 fans with random speeds for demonstration
            import random
            num_fans = random.randint(1, 3)
            for i in range(num_fans):
                fans.append({
                    'name': f'Fan {i+1}',
                    'speed': random.randint(800, 2200)  # RPM
                })
            return fans
        except:
            return [{'name': 'Fan 1', 'speed': 0}]
    
    def get_gpu_metrics(self):
        """Get GPU metrics - simulated since psutil doesn't have GPU support"""
        try:
            # For real GPU monitoring, you'd use libraries like GPUtil or nvidia-ml-py
            import random
            return {
                'gpu_usage': random.randint(0, 100),  # Simulated GPU usage %
                'gpu_frequency': random.randint(300, 1800),  # Simulated GPU MHz
                'gpu_memory_used': random.randint(0, 8000),  # Simulated MB
                'gpu_memory_total': 8192  # Simulated 8GB VRAM
            }
        except:
            return {
                'gpu_usage': 0,
                'gpu_frequency': 0,
                'gpu_memory_used': 0,
                'gpu_memory_total': 8192
            }
    
    def get_cached_metrics(self):
        current_time = time.time()
        if current_time - self.last_update > 0.9:  # Cache for 0.9 seconds
            self.cached_metrics = self._get_metrics()
            self.last_update = current_time
        return self.cached_metrics
    
    def _get_metrics(self):
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        self.cpu_history.append(cpu_percent)
        self.ram_history.append(ram.percent)
        
        gpu_metrics = self.get_gpu_metrics()
        fan_speeds = self.get_fan_speeds()
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'ram_percent': ram.percent,
            'ram_used': ram.used // (1024**3),  # GB
            'ram_total': ram.total // (1024**3),  # GB
            'disk_percent': psutil.disk_usage('/').percent,
            'vram_percent': psutil.swap_memory().percent,
            'temperature': self.get_cpu_temperature(),
            'cpu_history': list(self.cpu_history),
            'ram_history': list(self.ram_history),
            'gpu_usage': gpu_metrics['gpu_usage'],
            'gpu_frequency': gpu_metrics['gpu_frequency'],
            'gpu_memory_used': gpu_metrics['gpu_memory_used'],
            'gpu_memory_total': gpu_metrics['gpu_memory_total'],
            'fan_speeds': fan_speeds,
            'fan_count': len(fan_speeds)
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
        
    def draw_circle_meter(self, x, y, radius, value, color, width=8, text="", subtext=""):
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
        
        # Main text
        main_text = self.canvas.create_text(
            x, y - 10, 
            text=text, fill='white', font=('Arial', 12, 'bold')
        )
        
        # Subtext
        sub_text = self.canvas.create_text(
            x, y + 15, 
            text=subtext, fill=color, font=('Arial', 10)
        )
        
        return bg_circle, value_circle, main_text, sub_text
    
    def draw_vertical_bar(self, x, y, width, height, value, color, label="", max_value=100):
        """Draw a vertical progress bar"""
        bar_bottom = y + height
        
        # Background
        bg = self.canvas.create_rectangle(
            x - width//2, y, 
            x + width//2, bar_bottom, 
            outline='#333', fill='#333'
        )
        
        # Fill
        fill_height = (value / max_value) * height
        fill = self.canvas.create_rectangle(
            x - width//2, bar_bottom - fill_height, 
            x + width//2, bar_bottom, 
            fill=color
        )
        
        # Label
        label_text = self.canvas.create_text(
            x, y - 20, 
            text=label, fill='white', font=('Arial', 10)
        )
        
        # Value text
        value_text = self.canvas.create_text(
            x, bar_bottom + 20, 
            text=f"{value}", fill='white', font=('Arial', 9)
        )
        
        return bg, fill, label_text, value_text
    
    def update_circle(self, item_id, value):
        self.canvas.itemconfig(item_id, extent=-3.6 * value)
    
    def update_vertical_bar(self, fill_id, y, height, value, max_value=100):
        fill_height = (value / max_value) * height
        coords = self.canvas.coords(fill_id)
        if coords:
            self.canvas.coords(
                fill_id,
                coords[0], y + height - fill_height,
                coords[2], y + height
            )

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
        self.center_window(1400, 800)
        self.root.minsize(1200, 700)
        
        # Theme and state
        self.current_theme = 'dark'
        self.last_width = 0
        self.last_height = 0
        
        # Store widget references
        self.widgets = {
            'cpu': {}, 'ram': {}, 'gpu': {}, 'gpu_freq': {},
            'fans': [], 'left_bar': {}, 'right_bar': {}
        }
        
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
        canvas_width = self.canvas.winfo_width() or 1400
        canvas_height = self.canvas.winfo_height() or 800
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Clear previous widgets
        self.widgets = {key: {} for key in self.widgets}
        self.widgets['fans'] = []
        
        # System info at top
        self.widgets['info'] = self.canvas.create_text(
            center_x, 30, 
            text=f"CPU: {psutil.cpu_count()} Cores | RAM: {psutil.virtual_memory().total//(1024**3)}GB | GPU: {self.metrics_collector.get_cached_metrics().get('gpu_memory_total', 0)//1024}GB", 
            fill=Config.COLORS['text'], font=('Arial', 12), anchor='center'
        )
        
        # Left vertical bar - CPU Frequency (existing)
        left_bar_x = center_x - 400
        bar_height = 350
        bar_bottom = 150 + bar_height
        
        self.canvas.create_text(left_bar_x, 100, text="CPU Frequency", 
                               fill=Config.COLORS['text'], font=('Arial', 10), anchor='center')
        
        self.widgets['left_bar']['bg'] = self.canvas.create_rectangle(
            left_bar_x - 10, 150, 
            left_bar_x + 10, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.widgets['left_bar']['fill'] = self.canvas.create_rectangle(
            left_bar_x - 10, bar_bottom, 
            left_bar_x + 10, bar_bottom, 
            fill=Config.COLORS['frequency']
        )
        self.widgets['left_bar']['text'] = self.canvas.create_text(
            left_bar_x, bar_bottom + 20, 
            text="0.0 GHz", fill=Config.COLORS['text'], font=('Arial', 9)
        )
        
        # Right vertical bar - CPU Usage (existing)
        right_bar_x = center_x + 400
        
        self.canvas.create_text(right_bar_x, 100, text="CPU Usage", 
                               fill=Config.COLORS['text'], font=('Arial', 10), anchor='center')
        
        self.widgets['right_bar']['bg'] = self.canvas.create_rectangle(
            right_bar_x - 10, 150, 
            right_bar_x + 10, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.widgets['right_bar']['fill'] = self.canvas.create_rectangle(
            right_bar_x - 10, bar_bottom, 
            right_bar_x + 10, bar_bottom, 
            fill=Config.COLORS['cpu']
        )
        self.widgets['right_bar']['text'] = self.canvas.create_text(
            right_bar_x, bar_bottom + 20, 
            text="0%", fill=Config.COLORS['text'], font=('Arial', 9)
        )
        
        # Large CPU pie chart in center (existing)
        circle_radius = 100
        self.widgets['cpu']['bg'], self.widgets['cpu']['circle'], \
        self.widgets['cpu']['text'], self.widgets['cpu']['subtext'] = self.visualizer.draw_circle_meter(
            center_x, center_y - 50, circle_radius, 0, Config.COLORS['cpu'],
            text="CPU: 0%", subtext="0.0 GHz"
        )
        
        # New: RAM Usage circle (left of CPU)
        self.widgets['ram']['bg'], self.widgets['ram']['circle'], \
        self.widgets['ram']['text'], self.widgets['ram']['subtext'] = self.visualizer.draw_circle_meter(
            center_x - 200, center_y - 50, 80, 0, Config.COLORS['ram'],
            text="RAM: 0%", subtext="0/0 GB"
        )
        
        # New: GPU Usage circle (right of CPU)
        self.widgets['gpu']['bg'], self.widgets['gpu']['circle'], \
        self.widgets['gpu']['text'], self.widgets['gpu']['subtext'] = self.visualizer.draw_circle_meter(
            center_x + 200, center_y - 50, 80, 0, Config.COLORS['gpu'],
            text="GPU: 0%", subtext="0 MB"
        )
        
        # New: GPU Frequency circle (below GPU)
        self.widgets['gpu_freq']['bg'], self.widgets['gpu_freq']['circle'], \
        self.widgets['gpu_freq']['text'], self.widgets['gpu_freq']['subtext'] = self.visualizer.draw_circle_meter(
            center_x + 200, center_y + 150, 60, 0, Config.COLORS['gpu_freq'],
            text="GPU Freq", subtext="0 MHz", width=6
        )
        
        # New: Fan speeds (below CPU)
        fan_start_x = center_x - 150
        self.create_fan_displays(fan_start_x, center_y + 150, 300)
        
        # FPS counter
        self.widgets['fps'] = self.canvas.create_text(
            canvas_width - 50, 20, 
            text="FPS: 0", fill=Config.COLORS['text'], font=('Arial', 8), anchor='ne'
        )

    def create_fan_displays(self, start_x, y, total_width):
        """Create dynamic fan speed displays"""
        # For demonstration, we'll create 3 fan slots that will be populated dynamically
        fan_spacing = total_width // 4
        
        for i in range(3):
            fan_x = start_x + (i + 1) * fan_spacing
            
            # Fan circle
            bg, circle, text, subtext = self.visualizer.draw_circle_meter(
                fan_x, y, 50, 0, Config.COLORS['fan'],
                text=f"Fan {i+1}", subtext="0 RPM", width=6
            )
            
            self.widgets['fans'].append({
                'bg': bg, 'circle': circle, 'text': text, 'subtext': subtext,
                'x': fan_x, 'y': y
            })

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
            self.root.title(f"System Monitor - CPU: {metrics['cpu_percent']:.1f}% | RAM: {metrics['ram_percent']:.1f}% | GPU: {metrics['gpu_usage']:.1f}%")
            
            # Update FPS counter
            self.canvas.itemconfig(self.widgets['fps'], text=f"FPS: {1}")
            
            # Update visual elements
            self.update_visuals(metrics)
            
            # Check alerts
            alerts = self.alert_manager.check_thresholds(metrics)
            if alerts:
                self.handle_alerts(alerts)
                
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def update_visuals(self, metrics):
        # Update existing CPU elements
        self.visualizer.update_circle(self.widgets['cpu']['circle'], metrics['cpu_percent'])
        self.canvas.itemconfig(self.widgets['cpu']['text'], text=f"CPU: {metrics['cpu_percent']:.1f}%")
        self.canvas.itemconfig(self.widgets['cpu']['subtext'], text=f"{metrics['cpu_freq']/1000:.1f} GHz")
        
        # Update existing vertical bars
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 50 and canvas_height > 50:
            center_x = canvas_width // 2
            bar_height = 350
            bar_bottom = 150 + bar_height
            
            left_bar_x = center_x - 400
            right_bar_x = center_x + 400
            
            # Left vertical - CPU Frequency
            max_freq = self.metrics_collector.cached_metrics.get('max_freq', 4000)
            freq_height = (metrics['cpu_freq'] / max_freq) * bar_height
            self.canvas.coords(
                self.widgets['left_bar']['fill'], 
                left_bar_x - 10, bar_bottom - freq_height, 
                left_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.widgets['left_bar']['text'], text=f"{metrics['cpu_freq']/1000:.1f} GHz")
            
            # Right vertical - CPU Usage
            usage_height = (metrics['cpu_percent'] / 100) * bar_height
            self.canvas.coords(
                self.widgets['right_bar']['fill'], 
                right_bar_x - 10, bar_bottom - usage_height, 
                right_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.widgets['right_bar']['text'], text=f"{metrics['cpu_percent']:.1f}%")
        
        # NEW: Update RAM circle
        self.visualizer.update_circle(self.widgets['ram']['circle'], metrics['ram_percent'])
        self.canvas.itemconfig(self.widgets['ram']['text'], text=f"RAM: {metrics['ram_percent']:.1f}%")
        self.canvas.itemconfig(self.widgets['ram']['subtext'], text=f"{metrics['ram_used']}/{metrics['ram_total']} GB")
        
        # NEW: Update GPU circle
        self.visualizer.update_circle(self.widgets['gpu']['circle'], metrics['gpu_usage'])
        self.canvas.itemconfig(self.widgets['gpu']['text'], text=f"GPU: {metrics['gpu_usage']:.1f}%")
        self.canvas.itemconfig(self.widgets['gpu']['subtext'], text=f"{metrics['gpu_memory_used']} MB")
        
        # NEW: Update GPU Frequency circle
        gpu_freq_percent = (metrics['gpu_frequency'] / 1800) * 100  # Assuming 1800 MHz max
        self.visualizer.update_circle(self.widgets['gpu_freq']['circle'], gpu_freq_percent)
        self.canvas.itemconfig(self.widgets['gpu_freq']['subtext'], text=f"{metrics['gpu_frequency']} MHz")
        
        # NEW: Update Fan speeds
        self.update_fan_displays(metrics['fan_speeds'])

    def update_fan_displays(self, fan_speeds):
        """Update fan speed displays dynamically"""
        max_fan_speed = 3000  # Assume 3000 RPM max for visualization
        
        # Update existing fan displays
        for i, fan_widget in enumerate(self.widgets['fans']):
            if i < len(fan_speeds):
                # Show this fan
                fan = fan_speeds[i]
                fan_percent = (fan['speed'] / max_fan_speed) * 100
                
                self.visualizer.update_circle(fan_widget['circle'], fan_percent)
                self.canvas.itemconfig(fan_widget['text'], text=fan['name'])
                self.canvas.itemconfig(fan_widget['subtext'], text=f"{fan['speed']} RPM")
                
                # Make sure it's visible
                self.canvas.itemconfig(fan_widget['bg'], state=tk.NORMAL)
                self.canvas.itemconfig(fan_widget['circle'], state=tk.NORMAL)
                self.canvas.itemconfig(fan_widget['text'], state=tk.NORMAL)
                self.canvas.itemconfig(fan_widget['subtext'], state=tk.NORMAL)
            else:
                # Hide this fan slot
                self.canvas.itemconfig(fan_widget['bg'], state=tk.HIDDEN)
                self.canvas.itemconfig(fan_widget['circle'], state=tk.HIDDEN)
                self.canvas.itemconfig(fan_widget['text'], state=tk.HIDDEN)
                self.canvas.itemconfig(fan_widget['subtext'], state=tk.HIDDEN)

    def handle_alerts(self, alerts):
        for level, message in alerts:
            self.logger.warning(f"{level}: {message}")

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
                f.write(f"GPU Usage: {metrics['gpu_usage']:.1f}%\n")
                f.write(f"GPU Frequency: {metrics['gpu_frequency']} MHz\n")
                f.write(f"Fan Speeds: {[fan['speed'] for fan in metrics['fan_speeds']]} RPM\n")
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