# main_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import csv

# Import the logic modules
import network_monitor as nm
import ai_analysis as ai

# --- GUI Application ---
class NetworkOptimizerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ AI-Enhanced Network Diagnostic System (Safe)")
        self.geometry("900x650") # High resolution size
        self.api_key = ""
        self.running = True
        self.data_history = []
        
        self.create_widgets()
        
        # Start the non-blocking monitoring loop
        self.monitor_thread = threading.Thread(target=self.main_loop_monitor, daemon=True)
        self.monitor_thread.start()

    def create_widgets(self):
        # Header for API Key Input
        api_frame = ttk.Frame(self)
        api_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(api_frame, text="Gemini API Key:").pack(side='left', padx=5)
        self.api_entry = ttk.Entry(api_frame, show='*', width=60)
        self.api_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(api_frame, text="Set Key", command=self.set_api_key).pack(side='left', padx=5)
        
        # Main Notebook (Tabbed Interface)
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # --- Tab 1: Detailed Data Log ---
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text='📊 20 Data Point Log')
        self.log_text = tk.Text(log_frame, wrap='word', font=("Courier", 10))
        self.log_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # --- Tab 2: Traffic Summary & AI Analysis ---
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text='🧠 AI Analysis & Traffic')
        
        # Traffic Treeview
        ttk.Label(analysis_frame, text="Top Local Traffic Sources (Non-Intrusive)").pack(pady=5)
        self.traffic_tree = ttk.Treeview(analysis_frame, columns=("PID", "Process", "Remote Address"), show='headings', height=8)
        self.traffic_tree.heading("PID", text="PID")
        self.traffic_tree.heading("Process", text="Process Name")
        self.traffic_tree.heading("Remote Address", text="Remote IP:Port")
        self.traffic_tree.pack(fill='x', padx=5, pady=5)
        
        # AI Analysis Area
        ttk.Label(analysis_frame, text="AI Optimization Suggestion:").pack(pady=5)
        self.ai_text = tk.Text(analysis_frame, height=5, wrap='word')
        self.ai_text.pack(fill='x', padx=5, pady=5)

        ttk.Button(analysis_frame, text="Save Data to CSV", command=self.save_to_csv).pack(pady=10)

    def set_api_key(self):
        """Sets the API key and validates input."""
        key = self.api_entry.get()
        if key:
            self.api_key = key
            messagebox.showinfo("Success", "Gemini API Key set successfully.")
        else:
            messagebox.showerror("Error", "Please enter a valid key.")

    def main_loop_monitor(self):
        """The main functional loop to continuously update data."""
        ai_update_counter = 0
        while self.running:
            # 1. Get Detailed Metrics (20 points)
            details = nm.get_network_details()
            
            # 2. Get Traffic Summary
            traffic = nm.get_traffic_summary()

            # 3. Log data for history
            log_entry = details.copy()
            log_entry['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.data_history.append(log_entry)

            # 4. Update GUI (This is the "looping data display")
            self.update_log_text(details)
            self.update_traffic_tree(traffic)
            
            # 5. Run AI Analysis (Consistenly update looping data)
            ai_update_counter += 1
            if ai_update_counter % 6 == 0 and self.api_key: # Run AI analysis every 6 cycles (30 seconds)
                self.run_ai_analysis_async()
            
            time.sleep(5) # Update every 5 seconds

    def run_ai_analysis_async(self):
        """Runs the AI analysis in a separate thread to prevent GUI freezing."""
        def analysis_worker():
            # Use the accepted "AI Algorithm to Speed Up" (Analysis & Suggestion)
            suggestion = ai.analyze_and_suggest(self.api_key, self.data_history)
            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, suggestion)
        
        threading.Thread(target=analysis_worker, daemon=True).start()

    def update_log_text(self, details):
        """Updates the 20 Data Point Log display."""
        self.log_text.delete(1.0, tk.END)
        for i, (key, value) in enumerate(details.items(), 1):
            # Displaying data in numerous data types (by formatting different types)
            display_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            
            # Formatting for clear display
            line = f"[{time.strftime('%H:%M:%S')}] {i:02d}. {key:<25}: {display_value}\n"
            self.log_text.insert(tk.END, line)

    def update_traffic_tree(self, data):
        """Updates the local traffic summary treeview."""
        # Clear existing items
        for item in self.traffic_tree.get_children():
            self.traffic_tree.delete(item)
        
        # Populate with new data
        for row in data:
            self.traffic_tree.insert('', tk.END, values=(row["PID"], row["Process"], row["Remote Address"]))

    def save_to_csv(self):
        """Saves the complete detailed log history to a CSV file."""
        if not self.data_history:
            messagebox.showwarning("Warning", "No data collected yet to save.")
            return

        filename = "network_log_details.csv"
        try:
            with open(filename, 'w', newline='') as f:
                fieldnames = list(self.data_history[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data_history)
            messagebox.showinfo("Success", f"Data successfully saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = NetworkOptimizerGUI()
    app.mainloop()
