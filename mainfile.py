import tkinter as tk
from tkinter import ttk
import re
import math
import time

class PasswordChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Strength Checker")
        self.root.geometry("600x400")
        self.root.configure(bg="#2c3e50")

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="Password Strength Checker", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
        title_label.pack(pady=(0, 20))

        # Password Entry
        password_label = tk.Label(main_frame, text="Enter Password:", font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50")
        password_label.pack(anchor="w")
        
        self.password_entry = ttk.Entry(main_frame, font=("Helvetica", 14), show="*", width=40)
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)

        # Strength Indicator
        self.strength_label = tk.Label(main_frame, text="Strength: N/A", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.strength_label.pack(pady=(10, 5))

        self.strength_bar = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="determinate")
        self.strength_bar.pack(pady=5)
        
        # Time to Crack
        self.crack_time_label = tk.Label(main_frame, text="Time to Crack: N/A", font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50")
        self.crack_time_label.pack(pady=(5, 10))

        # Toggle Password Visibility
        self.show_password_var = tk.IntVar()
        self.show_password_checkbox = ttk.Checkbutton(main_frame, text="Show Password", 
                                                      variable=self.show_password_var, 
                                                      command=self.toggle_password_visibility)
        self.show_password_checkbox.pack()
        
    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def check_password_strength(self, event=None):
        password = self.password_entry.get()
        score = 0
        length = len(password)
        
        # Criteria for scoring
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_number = bool(re.search(r'[0-9]', password))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9\s]', password))
        
        # Base score on length
        if length > 8:
            score += 20
        if length > 12:
            score += 20
        if length > 16:
            score += 20
            
        # Add points for character diversity
        if has_lowercase: score += 10
        if has_uppercase: score += 10
        if has_number: score += 10
        if has_symbol: score += 10
            
        # Adjust score for complexity combinations
        character_types = sum([has_lowercase, has_uppercase, has_number, has_symbol])
        if character_types > 2:
            score += 15
        if character_types > 3:
            score += 15
            
        self.update_ui(score, password, length)

    def update_ui(self, score, password, length):
        # Update strength label and progress bar
        if length == 0:
            rating = "N/A"
            color = "#bdc3c7"
            bar_value = 0
        elif score < 40:
            rating = "Too Weak"
            color = "#e74c3c"  # Red
            bar_value = score
        elif score < 75:
            rating = "Moderate"
            color = "#f39c12"  # Orange
            bar_value = score
        else:
            rating = "Strong"
            color = "#27ae60"  # Green
            bar_value = score
            
        self.strength_label.config(text=f"Strength: {rating}", fg=color)
        self.strength_bar["value"] = bar_value
        
        # Update time to crack
        self.crack_time_label.config(text=self.estimate_crack_time(password))

    def estimate_crack_time(self, password):
        length = len(password)
        if length == 0:
            return "Time to Crack: N/A"

        # Character set sizes
        char_sets = 0
        if re.search(r'[a-z]', password): char_sets += 26
        if re.search(r'[A-Z]', password): char_sets += 26
        if re.search(r'[0-9]', password): char_sets += 10
        if re.search(r'[^a-zA-Z0-9\s]', password): char_sets += 32  # Common special characters

        if char_sets == 0:
            return "Time to Crack: Too short to estimate"

        # Calculate entropy (in bits)
        entropy = length * math.log2(char_sets)

        # Assume 10^12 guesses per second (a common benchmark for high-speed cracking)
        guesses_per_second = 10**12
        combinations = 2**entropy

        if combinations > guesses_per_second:
            seconds_to_crack = combinations / guesses_per_second
            return self.format_time(seconds_to_crack)
        else:
            return "Time to Crack: Instant"

    def format_time(self, seconds):
        if seconds < 60:
            return f"Time to Crack: {int(seconds)} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"Time to Crack: {int(minutes)} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"Time to Crack: {int(hours)} hours"
        elif seconds < 31536000:
            days = seconds // 86400
            return f"Time to Crack: {int(days)} days"
        else:
            years = seconds // 31536000
            return f"Time to Crack: {int(years)} years"

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordChecker(root)
    style = ttk.Style()
    style.theme_use('clam')  # Or 'vista', 'xpnative', 'alt', 'default' for a different look
    root.mainloop()
