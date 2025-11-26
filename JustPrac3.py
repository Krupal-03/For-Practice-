import tkinter as tk
import psutil

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.configure(bg='#1e1e1e')
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        
        # Get screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080
        
        self.canvas = tk.Canvas(root, bg='#1e1e1e', highlightthickness=0, 
                               width=self.screen_width, height=self.screen_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.cpu_freq = psutil.cpu_freq()
        self.max_freq = self.cpu_freq.max if self.cpu_freq else 4000
        
        self.create_display()
        self.update_metrics()

    def create_display(self):
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # System info at top
        self.canvas.create_text(center_x, 50, 
                               text=f"CPU: {psutil.cpu_count()} Cores | RAM: {psutil.virtual_memory().total//(1024**3)}GB | OS: {psutil.sys.platform}", 
                               fill='white', font=('Arial', 16), anchor='center')
        
        # Left vertical bar - CPU Frequency (positioned 400px left of center)
        left_bar_x = center_x - 400
        self.canvas.create_text(left_bar_x, 150, text="CPU Frequency", fill='white', font=('Arial', 14), anchor='center')
        self.vertical_left_bg = self.canvas.create_rectangle(left_bar_x - 25, 200, left_bar_x + 5, 700, outline='#333', fill='#333')
        self.vertical_left_fill = self.canvas.create_rectangle(left_bar_x - 25, 700, left_bar_x + 5, 700, fill='#ff9ff3')
        self.vertical_left_text = self.canvas.create_text(left_bar_x - 10, 730, text="0.0 GHz", fill='white', font=('Arial', 12))
        
        # Right vertical bar - CPU Usage (positioned 400px right of center)
        right_bar_x = center_x + 400
        self.canvas.create_text(right_bar_x, 150, text="CPU Usage", fill='white', font=('Arial', 14), anchor='center')
        self.vertical_right_bg = self.canvas.create_rectangle(right_bar_x - 25, 200, right_bar_x + 5, 700, outline='#333', fill='#333')
        self.vertical_right_fill = self.canvas.create_rectangle(right_bar_x - 25, 700, right_bar_x + 5, 700, fill='#ff6b6b')
        self.vertical_right_text = self.canvas.create_text(right_bar_x - 10, 730, text="0%", fill='white', font=('Arial', 12))
        
        # Large CPU pie chart in center (scaled up)
        circle_radius = 200  # Increased size
        self.cpu_circle_bg = self.canvas.create_arc(center_x - circle_radius, center_y - circle_radius, 
                                                   center_x + circle_radius, center_y + circle_radius, 
                                                   start=90, extent=359.9, outline='#333', width=12, style=tk.ARC)
        self.cpu_circle = self.canvas.create_arc(center_x - circle_radius, center_y - circle_radius, 
                                                center_x + circle_radius, center_y + circle_radius, 
                                                start=90, extent=0, outline='#ff6b6b', width=12, style=tk.ARC)
        self.cpu_text = self.canvas.create_text(center_x, center_y - 30, text="CPU: 0%", fill='white', font=('Arial', 24, 'bold'))
        self.cpu_freq_text = self.canvas.create_text(center_x, center_y + 20, text="0.0 GHz", fill='#ff9ff3', font=('Arial', 18))

    def update_metrics(self):
        # Get metrics
        cpu_pct = psutil.cpu_percent()
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        # Update large CPU pie chart
        self.canvas.itemconfig(self.cpu_circle, extent=-3.6 * cpu_pct)
        self.canvas.itemconfig(self.cpu_text, text=f"CPU: {cpu_pct:.1f}%")
        self.canvas.itemconfig(self.cpu_freq_text, text=f"{freq/1000:.1f} GHz")
        
        # Update vertical bars
        center_x = self.screen_width // 2
        left_bar_x = center_x - 400
        right_bar_x = center_x + 400
        
        # Left vertical - CPU Frequency (grows upward from bottom)
        freq_height = (freq / self.max_freq) * 500  # 500px height for bars
        self.canvas.coords(self.vertical_left_fill, left_bar_x - 25, 700 - freq_height, left_bar_x + 5, 700)
        self.canvas.itemconfig(self.vertical_left_text, text=f"{freq/1000:.1f} GHz")
        
        # Right vertical - CPU Usage (grows upward from bottom)
        usage_height = (cpu_pct / 100) * 500  # 500px height for bars
        self.canvas.coords(self.vertical_right_fill, right_bar_x - 25, 700 - usage_height, right_bar_x + 5, 700)
        self.canvas.itemconfig(self.vertical_right_text, text=f"{cpu_pct:.1f}%")
        
        self.root.after(1000, self.update_metrics)

if __name__ == "__main__":
    root = tk.Tk()
    SystemMonitor(root)
    root.mainloop()