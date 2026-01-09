import sys
import subprocess
import os
import time
import traceback # Added for error logging

# --- CRITICAL FIX: Force Working Directory ---
# When double-clicking, Windows sometimes runs from System32. This fixes it.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_and_install_dependencies():
    required = {
        'pydirectinput': 'pydirectinput', 
        'pynput': 'pynput', 
        'pyautogui': 'pyautogui'
    }
    missing = []

    for lib, package in required.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"\n[!] Missing required libraries: {', '.join(missing)}")
        print("    To run this script, these must be installed.")
        
        while True:
            try:
                choice = input("    Do you want to install them now? (y/n): ").strip().lower()
            except EOFError:
                choice = 'n' # Handle rare input errors

            if choice == 'y':
                print("\n[...] Installing dependencies...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                    print("[+] Installation successful!")
                    input("\n    Press Enter to restart the application...")
                    subprocess.Popen([sys.executable] + sys.argv)
                    sys.exit()
                except subprocess.CalledProcessError as e:
                    print(f"\n[!] Error during installation: {e}")
                    input("Press Enter to exit...")
                    sys.exit()
            elif choice == 'n':
                sys.exit()

# Wrap the check in a try/except to catch "instant close" errors
try:
    check_and_install_dependencies()
except Exception as e:
    print("\nCRITICAL ERROR DURING STARTUP:")
    traceback.print_exc()
    input("\nPress Enter to close...")
    sys.exit()

check_and_install_dependencies()

# --- 2. MAIN IMPORTS ---
import pydirectinput
import random
import threading
import json  # Added for config file
from pynput import mouse
from datetime import datetime
import pyautogui
import tkinter as tk
from tkinter import ttk

# --- Configuration Globals ---
IDLE_THRESHOLD = 5.0    
last_activity_time = time.time()
script_enabled = False
is_script_moving = False 
next_movement_time = None

pydirectinput.FAILSAFE = False 

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def on_move(x, y):
    global last_activity_time
    if not is_script_moving:
        last_activity_time = time.time()

listener = mouse.Listener(on_move=on_move)      
listener.start()

class MouseMoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Mover v1.0.8")
        self.root.geometry("500x600") # Increased height slightly for new button
        self.root.resizable(False, False)
        
        # Configuration variables (Defaults)
        self.min_idle_trigger = tk.DoubleVar(value=8.0)
        self.max_idle_trigger = tk.DoubleVar(value=20.0)
        self.min_wait_time = tk.DoubleVar(value=25.0)
        self.max_wait_time = tk.DoubleVar(value=45.0)
        self.x_move_limit = tk.IntVar(value=150)
        self.y_move_limit = tk.IntVar(value=40)
        self.min_duration = tk.DoubleVar(value=0.2)
        self.max_duration = tk.DoubleVar(value=0.4)
        
        # --- LOAD CONFIGURATION FROM FILE ---
        self.load_config()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="SIMPLE MOUSE MOVER", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status display
        self.status_label = ttk.Label(main_frame, text="Status: PAUSED", font=("Arial", 12))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Countdown display
        self.countdown_label = ttk.Label(main_frame, text="", font=("Arial", 10), foreground="blue")
        self.countdown_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="START", command=self.start_script, width=15)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="STOP", command=self.stop_script, width=15)
        self.stop_btn.grid(row=0, column=1, padx=5)
        self.stop_btn.state(['disabled'])
        
        # Settings section
        settings_label = ttk.Label(main_frame, text="Settings:", font=("Arial", 11, "bold"))
        settings_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        settings_frame = ttk.LabelFrame(main_frame, text="Movement Configuration", padding="10")
        settings_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Idle Trigger Range
        ttk.Label(settings_frame, text="Idle Trigger (s):").grid(row=0, column=0, sticky=tk.W, pady=2)
        idle_frame = ttk.Frame(settings_frame)
        idle_frame.grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Entry(idle_frame, textvariable=self.min_idle_trigger, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(idle_frame, text="to").pack(side=tk.LEFT, padx=2)
        ttk.Entry(idle_frame, textvariable=self.max_idle_trigger, width=8).pack(side=tk.LEFT, padx=2)
        
        # Wait Time Range
        ttk.Label(settings_frame, text="Wait Time (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        wait_frame = ttk.Frame(settings_frame)
        wait_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Entry(wait_frame, textvariable=self.min_wait_time, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(wait_frame, text="to").pack(side=tk.LEFT, padx=2)
        ttk.Entry(wait_frame, textvariable=self.max_wait_time, width=8).pack(side=tk.LEFT, padx=2)
        
        # Movement Limits
        ttk.Label(settings_frame, text="X Move Limit (px):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.x_move_limit, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(settings_frame, text="Y Move Limit (px):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.y_move_limit, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Duration Range
        ttk.Label(settings_frame, text="Duration (s):").grid(row=4, column=0, sticky=tk.W, pady=2)
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.grid(row=4, column=1, sticky=tk.W, pady=2)
        ttk.Entry(duration_frame, textvariable=self.min_duration, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(duration_frame, text="to").pack(side=tk.LEFT, padx=2)
        ttk.Entry(duration_frame, textvariable=self.max_duration, width=8).pack(side=tk.LEFT, padx=2)
        
        # --- NEW SAVE BUTTON ---
        save_btn = ttk.Button(settings_frame, text="Save Current Config", command=self.save_current_config)
        save_btn.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))

        # Log display
        log_label = ttk.Label(main_frame, text="Activity Log:", font=("Arial", 10, "bold"))
        log_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Log text box with scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=8, width=55, state='disabled', 
                                yscrollcommand=scrollbar.set, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Start auto mover thread
        threading.Thread(target=self.auto_mover_loop, daemon=True).start()
        # Start countdown update thread
        threading.Thread(target=self.update_countdown, daemon=True).start()

    # --- CONFIGURATION METHODS ---
    def load_config(self):
        """Loads config from m_cfg.txt or creates defaults."""
        default_config = {
            "min_idle": 8.0, "max_idle": 20.0,
            "min_wait": 25.0, "max_wait": 45.0,
            "x_limit": 150, "y_limit": 40,
            "min_dur": 0.2, "max_dur": 0.4
        }

        if not os.path.exists("m_cfg.txt"):
            self.save_config_file(default_config)
            data = default_config
        else:
            try:
                with open("m_cfg.txt", "r") as f:
                    data = json.load(f)
            except Exception:
                data = default_config

        # Apply values
        self.min_idle_trigger.set(data.get("min_idle", 8.0))
        self.max_idle_trigger.set(data.get("max_idle", 20.0))
        self.min_wait_time.set(data.get("min_wait", 25.0))
        self.max_wait_time.set(data.get("max_wait", 45.0))
        self.x_move_limit.set(data.get("x_limit", 150))
        self.y_move_limit.set(data.get("y_limit", 40))
        self.min_duration.set(data.get("min_dur", 0.2))
        self.max_duration.set(data.get("max_dur", 0.4))

    def save_current_config(self):
        """Saves current GUI values to file."""
        data = {
            "min_idle": self.min_idle_trigger.get(),
            "max_idle": self.max_idle_trigger.get(),
            "min_wait": self.min_wait_time.get(),
            "max_wait": self.max_wait_time.get(),
            "x_limit": self.x_move_limit.get(),
            "y_limit": self.y_move_limit.get(),
            "min_dur": self.min_duration.get(),
            "max_dur": self.max_duration.get()
        }
        self.save_config_file(data)
        self.log_message(">> Configuration saved to m_cfg.txt")

    def save_config_file(self, data):
        try:
            with open("m_cfg.txt", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log_message(f"Error saving config: {e}")

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{get_time()}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def start_script(self):
        global script_enabled
        script_enabled = True
        self.status_label.config(text="Status: ACTIVE", foreground="green")
        self.start_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.log_message("SYSTEM: ACTIVE")
    
    def stop_script(self):
        global script_enabled, next_movement_time
        script_enabled = False
        next_movement_time = None
        self.status_label.config(text="Status: PAUSED", foreground="red")
        self.countdown_label.config(text="")
        self.start_btn.state(['!disabled'])
        self.stop_btn.state(['disabled'])
        self.log_message("SYSTEM: PAUSED")
    
    def update_countdown(self):
        global script_enabled, last_activity_time, IDLE_THRESHOLD, next_movement_time
        
        while True:
            if script_enabled:
                elapsed_idle = time.time() - last_activity_time
                
                if elapsed_idle < IDLE_THRESHOLD:
                    remaining = IDLE_THRESHOLD - elapsed_idle
                    self.countdown_label.config(
                        text=f"⏸ Movement detected - resuming in {remaining:.1f}s",
                        foreground="orange"
                    )
                else:
                    if next_movement_time is not None:
                        time_until_movement = next_movement_time - time.time()
                        if time_until_movement > 0:
                            self.countdown_label.config(
                                text=f"⏳ Next movement in {time_until_movement:.1f}s",
                                foreground="green"
                            )
                        else:
                            self.countdown_label.config(text="🔄 Moving...", foreground="blue")
                    else:
                        self.countdown_label.config(text="⏳ Calculating next movement...", foreground="green")
            else:
                self.countdown_label.config(text="")
            
            time.sleep(0.1)
    
    def auto_mover_loop(self):
        global script_enabled, is_script_moving, IDLE_THRESHOLD, next_movement_time
        
        while True:
            if script_enabled:
                elapsed_idle = time.time() - last_activity_time
                
                if elapsed_idle > IDLE_THRESHOLD:
                    self.log_message("!! Status: IDLE. Quick-look triggered...")
                    is_script_moving = True  
                    
                    x_limit = self.x_move_limit.get()
                    y_limit = self.y_move_limit.get()
                    x_move = random.randint(-x_limit, x_limit)
                    y_move = random.randint(-y_limit, y_limit)
                    flick_duration = random.uniform(self.min_duration.get(), self.max_duration.get())
                    
                    try:
                        # FIXED: Removed 'tween' argument to prevent crash
                        pydirectinput.moveRel(x_move, y_move, relative=True, 
                                              duration=flick_duration)
                        self.log_message(f">> Success: Flicked {x_move}px, {y_move}px.")
                    except Exception as e:
                        self.log_message(f"ERROR: {e}")
                    
                    is_script_moving = False 
                    
                    IDLE_THRESHOLD = random.uniform(self.min_idle_trigger.get(), self.max_idle_trigger.get())
                    sleep_time = random.uniform(self.min_wait_time.get(), self.max_wait_time.get())
                    next_movement_time = time.time() + sleep_time
                    self.log_message(f".. Next Trigger: {round(IDLE_THRESHOLD, 1)}s | Wait: {round(sleep_time, 1)}s")
                    time.sleep(sleep_time)
                    next_movement_time = None
            else:
                next_movement_time = None
            
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        # Create and run GUI
        root = tk.Tk()
        app = MouseMoverGUI(root)
        root.mainloop()
    except Exception as e:
        # This catches crashes during the GUI runtime
        import traceback
        print("\nCRITICAL ERROR:")
        traceback.print_exc()

        input("\nPress Enter to exit...")
