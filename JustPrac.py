import tkinter as tk
import psutil

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.configure(bg='#1e1e1e')
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        
        self.canvas = tk.Canvas(root, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.cpu_freq = psutil.cpu_freq()
        self.max_freq = self.cpu_freq.max if self.cpu_freq else 4000
        self.metrics = [
            {"name": "CPU", "color": "#ff6b6b", "value": 0, "text": "0%"},
            {"name": "RAM", "color": "#4ecdc4", "value": 0, "text": "0%"},
            {"name": "VRAM", "color": "#45b7d1", "value": 0, "text": "0%"},
            {"name": "DISK", "color": "#96ceb4", "value": 0, "text": "0%"},
            {"name": "FREQ", "color": "#ff9ff3", "value": 0, "text": "0GHz"},
            {"name": "TEMP", "color": "#feca57", "value": 0, "text": "0°C"}
        ]
        
        self.bars = []
        self.create_display()
        self.update_metrics()

    def create_display(self):
        # System info
        self.canvas.create_text(50, 30, text=f"CPU: {psutil.cpu_count()}c | RAM: {psutil.virtual_memory().total//(1024**3)}GB", 
                               fill='white', font=('Arial', 12), anchor='w')
        
        # Progress bars grid
        for i, metric in enumerate(self.metrics):
            x, y = 150 + (i % 3) * 200, 150 + (i // 3) * 150
            bar = self.canvas.create_arc(x-50, y-50, x+50, y+50, start=90, extent=0, 
                                       outline=metric["color"], width=6, style=tk.ARC)
            self.canvas.create_text(x, y+60, text=metric["name"], fill='white', font=('Arial', 10))
            text_id = self.canvas.create_text(x, y-60, text="0%", fill='white', font=('Arial', 12))
            self.bars.append((bar, text_id))
        
        # GHz bars
        self.ghz_left = self.canvas.create_rectangle(50, 400, 250, 430, outline='#ff9ff3', width=2)
        self.ghz_left_fill = self.canvas.create_rectangle(50, 400, 50, 430, fill='#ff9ff3')
        self.ghz_left_text = self.canvas.create_text(150, 415, text="0.0 GHz", fill='white', font=('Arial', 10))
        
        self.ghz_right = self.canvas.create_rectangle(450, 400, 650, 430, outline='#ff6b6b', width=2)
        self.ghz_right_fill = self.canvas.create_rectangle(450, 400, 450, 430, fill='#ff6b6b')
        self.ghz_right_text = self.canvas.create_text(550, 415, text="0%", fill='white', font=('Arial', 10))

    def update_metrics(self):
        # Get metrics
        cpu_pct = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        try:
            temp = psutil.sensors_temperatures().get('coretemp', [None])[0].current or 0
        except:
            temp = 0
        
        # Update metrics data
        values = [cpu_pct, ram.percent, psutil.swap_memory().percent, disk.percent, 
                 (freq / self.max_freq) * 100, min(temp, 100)]
        
        # Update circular bars
        for i, (value, metric) in enumerate(zip(values, self.metrics)):
            bar, text_id = self.bars[i]
            self.canvas.itemconfig(bar, extent=-3.6 * min(value, 100))
            text = f"{freq/1000:.1f}GHz" if i == 4 else f"{temp:.0f}°C" if i == 5 else f"{value:.1f}%"
            self.canvas.itemconfig(text_id, text=text)
        
        # Update GHz bars
        self.canvas.coords(self.ghz_left_fill, 50, 400, 50 + (freq / self.max_freq) * 200, 430)
        self.canvas.itemconfig(self.ghz_left_text, text=f"{freq/1000:.1f} GHz")
        
        self.canvas.coords(self.ghz_right_fill, 450, 400, 450 + cpu_pct * 2, 430)
        self.canvas.itemconfig(self.ghz_right_text, text=f"{cpu_pct:.1f}%")
        
        self.root.after(1000, self.update_metrics)

if __name__ == "__main__":
    root = tk.Tk()
    SystemMonitor(root)
    root.mainloop()