import tkinter as tk
import psutil

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.configure(bg='#1e1e1e')
        
        # Set initial window size and center it
        window_width = 1000
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        self.center_window(window_width, window_height)
        
        self.canvas = tk.Canvas(root, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.cpu_freq = psutil.cpu_freq()
        self.max_freq = self.cpu_freq.max if self.cpu_freq else 4000
        
        # Track if we need to recreate display
        self.last_width = 0
        self.last_height = 0
        
        self.create_display()
        self.update_metrics()
        
        # Bind resize event with delay to avoid multiple calls
        self.root.bind('<Configure>', self.on_resize)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_resize(self, event):
        # Only respond to main window resize
        if event.widget == self.root:
            # Get current window size
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            # Only recreate if size actually changed significantly
            if (abs(current_width - self.last_width) > 10 or 
                abs(current_height - self.last_height) > 10):
                self.last_width = current_width
                self.last_height = current_height
                self.root.after(100, self.reposition_widgets)

    def reposition_widgets(self):
        self.canvas.delete("all")
        self.create_display()

    def create_display(self):
        # Get current canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Use default if canvas not yet rendered
        if canvas_width < 50 or canvas_height < 50:
            canvas_width = 1000
            canvas_height = 700
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Calculate sizes based on window size
        circle_radius = min(canvas_width, canvas_height) // 5
        bar_width = 20
        bar_height = min(400, canvas_height - 250)  # Limit bar height
        bar_spacing = min(300, canvas_width // 3)   # Limit bar spacing
        
        # System info at top
        self.canvas.create_text(
            center_x, 30, 
            text=f"CPU: {psutil.cpu_count()} Cores | RAM: {psutil.virtual_memory().total//(1024**3)}GB", 
            fill='white', font=('Arial', 12), anchor='center'
        )
        
        # Left vertical bar - CPU Frequency
        left_bar_x = center_x - bar_spacing
        bar_bottom = 150 + bar_height
        
        self.canvas.create_text(left_bar_x, 100, text="CPU Frequency", fill='white', font=('Arial', 10), anchor='center')
        self.left_bg = self.canvas.create_rectangle(
            left_bar_x - bar_width//2, 150, 
            left_bar_x + bar_width//2, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.left_fill = self.canvas.create_rectangle(
            left_bar_x - bar_width//2, bar_bottom, 
            left_bar_x + bar_width//2, bar_bottom, 
            fill='#ff9ff3'
        )
        self.left_text = self.canvas.create_text(
            left_bar_x, bar_bottom + 20, 
            text="0.0 GHz", fill='white', font=('Arial', 9)
        )
        
        # Right vertical bar - CPU Usage
        right_bar_x = center_x + bar_spacing
        
        self.canvas.create_text(right_bar_x, 100, text="CPU Usage", fill='white', font=('Arial', 10), anchor='center')
        self.right_bg = self.canvas.create_rectangle(
            right_bar_x - bar_width//2, 150, 
            right_bar_x + bar_width//2, bar_bottom, 
            outline='#333', fill='#333'
        )
        self.right_fill = self.canvas.create_rectangle(
            right_bar_x - bar_width//2, bar_bottom, 
            right_bar_x + bar_width//2, bar_bottom, 
            fill='#ff6b6b'
        )
        self.right_text = self.canvas.create_text(
            right_bar_x, bar_bottom + 20, 
            text="0%", fill='white', font=('Arial', 9)
        )
        
        # Large CPU pie chart in center
        self.cpu_bg = self.canvas.create_arc(
            center_x - circle_radius, center_y - circle_radius, 
            center_x + circle_radius, center_y + circle_radius, 
            start=90, extent=359.9, outline='#333', width=8, style=tk.ARC
        )
        self.cpu_circle = self.canvas.create_arc(
            center_x - circle_radius, center_y - circle_radius, 
            center_x + circle_radius, center_y + circle_radius, 
            start=90, extent=0, outline='#ff6b6b', width=8, style=tk.ARC
        )
        self.cpu_text = self.canvas.create_text(
            center_x, center_y - 20, 
            text="CPU: 0%", fill='white', font=('Arial', 16, 'bold')
        )
        self.cpu_freq_text = self.canvas.create_text(
            center_x, center_y + 15, 
            text="0.0 GHz", fill='#ff9ff3', font=('Arial', 12)
        )

    def update_metrics(self):
        # Get metrics
        cpu_pct = psutil.cpu_percent()
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        # Update large CPU pie chart
        self.canvas.itemconfig(self.cpu_circle, extent=-3.6 * cpu_pct)
        self.canvas.itemconfig(self.cpu_text, text=f"CPU: {cpu_pct:.1f}%")
        self.canvas.itemconfig(self.cpu_freq_text, text=f"{freq/1000:.1f} GHz")
        
        # Get current dimensions for bar updates
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 50 and canvas_height > 50:  # Only update if canvas is ready
            center_x = canvas_width // 2
            bar_height = min(400, canvas_height - 250)
            bar_spacing = min(300, canvas_width // 3)
            bar_bottom = 150 + bar_height
            
            left_bar_x = center_x - bar_spacing
            right_bar_x = center_x + bar_spacing
            
            # Left vertical - CPU Frequency
            freq_height = (freq / self.max_freq) * bar_height
            self.canvas.coords(
                self.left_fill, 
                left_bar_x - 10, bar_bottom - freq_height, 
                left_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.left_text, text=f"{freq/1000:.1f} GHz")
            
            # Right vertical - CPU Usage
            usage_height = (cpu_pct / 100) * bar_height
            self.canvas.coords(
                self.right_fill, 
                right_bar_x - 10, bar_bottom - usage_height, 
                right_bar_x + 10, bar_bottom
            )
            self.canvas.itemconfig(self.right_text, text=f"{cpu_pct:.1f}%")
        
        self.root.after(1000, self.update_metrics)

if __name__ == "__main__":
    root = tk.Tk()
    SystemMonitor(root)
    root.mainloop()