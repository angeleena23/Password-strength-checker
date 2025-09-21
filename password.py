import tkinter as tk
from tkinter import ttk
import re
import math
import time
import os
import csv
from urllib.request import urlopen, Request
import json

class PasswordChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Strength Checker")
        self.root.geometry("800x600")
        self.root.configure(bg="#e6e6fa")  # Light lavender background

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#e6e6fa")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Main content card
        card_frame = tk.Frame(main_frame, bg="#f9f9f9", bd=2, relief="groove")
        card_frame.pack(pady=50, padx=20, ipadx=20, ipady=20)

        # Title
        title_label = tk.Label(card_frame, text="How Secure is My Password?", font=("Helvetica", 24, "bold"), fg="#444444", bg="#f9f9f9")
        title_label.pack(pady=(0, 20))

        # Password Entry and toggle
        password_label = tk.Label(card_frame, text="Take a moment to check if your password is a weak link.", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        password_label.pack(anchor="w")
        
        entry_frame = tk.Frame(card_frame, bg="#f9f9f9")
        entry_frame.pack(pady=10, fill="x")

        self.password_entry = ttk.Entry(entry_frame, font=("Helvetica", 16), show="*", width=35)
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)

        # Toggle Password Visibility
        self.show_password_var = tk.IntVar()
        self.show_password_checkbox = ttk.Checkbutton(entry_frame, text="Show",
                                                      variable=self.show_password_var,
                                                      command=self.toggle_password_visibility)
        self.show_password_checkbox.pack(side="right", padx=5)

        # Strength Indicator
        self.strength_label = tk.Label(card_frame, text="Password strength: N/A", font=("Helvetica", 14, "bold"), fg="#555555", bg="#f9f9f9")
        self.strength_label.pack(pady=(10, 5), anchor="w")

        self.strength_bar = ttk.Progressbar(card_frame, orient="horizontal", length=300, mode="determinate")
        self.strength_bar.pack(pady=5, anchor="w")
        
        # Time to Crack
        self.crack_time_label = tk.Label(card_frame, text="Time to crack your password: N/A", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.crack_time_label.pack(pady=(5, 10), anchor="w")

        # Suggestions Frame
        self.suggestions_frame = tk.Frame(card_frame, bg="#f9f9f9")
        self.suggestions_frame.pack(fill="x", pady=10)
        
        suggestions_title = tk.Label(self.suggestions_frame, text="Password Composition", font=("Helvetica", 14, "bold"), fg="#444444", bg="#f9f9f9")
        suggestions_title.pack(anchor="w")

        self.length_label = tk.Label(self.suggestions_frame, text="⚪ At least 12 characters", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.length_label.pack(anchor="w", pady=2)

        self.lowercase_label = tk.Label(self.suggestions_frame, text="⚪ Lowercase", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.lowercase_label.pack(anchor="w", pady=2)

        self.uppercase_label = tk.Label(self.suggestions_frame, text="⚪ Uppercase", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.uppercase_label.pack(anchor="w", pady=2)

        self.symbol_label = tk.Label(self.suggestions_frame, text="⚪ Symbols (!?@...)", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.symbol_label.pack(anchor="w", pady=2)
        
        self.number_label = tk.Label(self.suggestions_frame, text="⚪ Numbers", font=("Helvetica", 12), fg="#555555", bg="#f9f9f9")
        self.number_label.pack(anchor="w", pady=2)

        self.leaked_password_label = tk.Label(card_frame, text="", font=("Helvetica", 12), fg="#e74c3c", bg="#f9f9f9")
        self.leaked_password_label.pack(pady=(10, 0), fill="x", anchor="w")

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
        
    def check_password_strength(self, event=None):
        password = self.password_entry.get()
        score = 0
        length = len(password)
        
        if ' ' in password:
            self.leaked_password_label.config(text="Warning: Spaces are not allowed in your password.", fg="#e74c3c")
            self.update_ui(0, password, 0)
            return

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
        self.update_suggestions(password)

    def update_ui(self, score, password, length):
        # Update strength label and progress bar
        if length == 0:
            rating = "N/A"
            color = "#bdc3c7"
            bar_value = 0
        elif score < 40:
            rating = "WEAK"
            color = "#e74c3c"  # Red
            bar_value = score
        elif score < 75:
            rating = "MODERATE"
            color = "#f39c12"  # Orange
            bar_value = score
        else:
            rating = "STRONG"
            color = "#27ae60"  # Green
            bar_value = score
            
        self.strength_label.config(text=f"Password strength: {rating}", fg=color)
        self.strength_bar["value"] = bar_value
        
        # Update time to crack
        self.crack_time_label.config(text=self.estimate_crack_time(password))

    def update_suggestions(self, password):
        length = len(password)
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_number = bool(re.search(r'[0-9]', password))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9\s]', password))
        
        self.length_label.config(text=f"{'✓' if length >= 12 else '⚪'} At least 12 characters", 
                                 fg="#27ae60" if length >= 12 else "#555555")
        self.lowercase_label.config(text=f"{'✓' if has_lowercase else '⚪'} Lowercase",
                                     fg="#27ae60" if has_lowercase else "#555555")
        self.uppercase_label.config(text=f"{'✓' if has_uppercase else '⚪'} Uppercase",
                                     fg="#27ae60" if has_uppercase else "#555555")
        self.symbol_label.config(text=f"{'✓' if has_symbol else '⚪'} Symbols (!?@...)",
                                  fg="#27ae60" if has_symbol else "#555555")
        self.number_label.config(text=f"{'✓' if has_number else '⚪'} Numbers",
                                 fg="#27ae60" if has_number else "#555555")

    def estimate_crack_time(self, password):
        length = len(password)
        if length == 0:
            return "Time to crack: N/A"

        # Character set sizes
        char_sets = 0
        if re.search(r'[a-z]', password): char_sets += 26
        if re.search(r'[A-Z]', password): char_sets += 26
        if re.search(r'[0-9]', password): char_sets += 10
        if re.search(r'[^a-zA-Z0-9\s]', password): char_sets += 32 

        if char_sets == 0:
            return "Time to crack: Too short to estimate"

        # Calculate entropy (in bits)
        entropy = length * math.log2(char_sets)

        # Assume 10^12 guesses per second (a common benchmark for high-speed cracking)
        guesses_per_second = 10**12
        combinations = 2**entropy

        if combinations > guesses_per_second:
            seconds_to_crack = combinations / guesses_per_second
            return self.format_time(seconds_to_crack)
        else:
            return "Time to crack: Instant"

    def format_time(self, seconds):
        if seconds < 60:
            return f"Time to crack: {int(seconds)} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"Time to crack: {int(minutes)} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"Time to crack: {int(hours)} hours"
        elif seconds < 31536000:
            days = seconds // 86400
            return f"Time to crack: {int(days)} days"
        else:
            years = seconds // 31536000
            return f"Time to crack: {int(years)} years"

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordChecker(root)
    
    # Custom style to match the provided image
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#e6e6fa")
    style.configure("TEntry", fieldbackground="#ffffff", relief="flat", borderwidth=1, focuscolor="#cccccc")
    style.configure("TProgressbar", thickness=10, background="#27ae60", troughcolor="#ecf0f1", relief="flat")
    
    root.mainloop()
