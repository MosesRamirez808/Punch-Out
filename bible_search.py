import tkinter as tk
from tkinter import scrolledtext
from freebible import read_web
import re
import threading
from PIL import Image, ImageTk  # Pillow for image support

def load_web_bible():
    bible = read_web()
    verses = []
    pattern = re.compile(r'^\[([^\]]+)\]\s*(.*)$')

    for book in bible:
        for chapter in book:
            for verse in chapter:
                verse_str = str(verse)
                m = pattern.match(verse_str)
                if m:
                    reference = m.group(1).strip()
                    text = m.group(2).strip()
                else:
                    reference = ""
                    text = verse_str.strip()
                verses.append((reference, text))
    return verses

def search_verses(verses, query):
    query_lower = query.lower()
    return [(ref, text) for (ref, text) in verses if query_lower in text.lower()]

class BibleSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bible Verse Search")
        self.geometry("600x550")  # Increased height for images
        self.resizable(False, False)

        # Load images
        self.load_images()

        # Top cross image
        if self.cross_img:
            cross_label = tk.Label(self, image=self.cross_img, bg="white")
            cross_label.pack(pady=5)

        # Loading label
        self.loading_label = tk.Label(self, text="📖 Loading Bible...", font=("Arial", 12))
        self.loading_label.pack(pady=10)

        # Search input
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(pady=5)

        tk.Label(self.search_frame, text="Enter topic or phrase:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.query_entry = tk.Entry(self.search_frame, width=40, font=("Arial", 10))
        self.query_entry.pack(side=tk.LEFT, padx=5)
        self.query_entry.bind("<Return>", self.perform_search)  # Enter key triggers search

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT, padx=5)
        self.search_button.config(state=tk.DISABLED)  # disabled until loaded

        # Results area
        self.results_text = scrolledtext.ScrolledText(self, width=70, height=20, wrap=tk.WORD, font=("Arial", 10))
        self.results_text.pack(padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)

        # Bottom Bible image
        if self.bible_img:
            bible_label = tk.Label(self, image=self.bible_img, bg="white")
            bible_label.pack(pady=5)

        # Close button
        self.close_button = tk.Button(self, text="Exit", command=self.destroy)
        self.close_button.pack(pady=5)

        # Load Bible in thread
        self.verses = []
        threading.Thread(target=self.load_bible_thread, daemon=True).start()

    def load_images(self):
        try:
            cross = Image.open("cross.png").resize((50, 50), Image.ANTIALIAS)
            self.cross_img = ImageTk.PhotoImage(cross)
        except Exception as e:
            print("Error loading cross.png:", e)
            self.cross_img = None

        try:
            bible = Image.open("bible.png").resize((60, 40), Image.ANTIALIAS)
            self.bible_img = ImageTk.PhotoImage(bible)
        except Exception as e:
            print("Error loading bible.png:", e)
            self.bible_img = None

    def load_bible_thread(self):
        self.verses = load_web_bible()
        self.after(0, self.bible_loaded)

    def bible_loaded(self):
        self.loading_label.config(text=f"✅ Loaded {len(self.verses)} verses.")
        self.search_button.config(state=tk.NORMAL)
        self.query_entry.focus_set()

    def perform_search(self, event=None):
        query = self.query_entry.get().strip()
        if not query:
            return
        results = search_verses(self.verses, query)

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)

        if results:
            self.results_text.insert(tk.END, f"✅ Found {len(results)} verse(s) containing: '{query}'\n\n")
            for ref, text in results:
                if ref:
                    self.results_text.insert(tk.END, f"{ref}: {text}\n")
                else:
                    self.results_text.insert(tk.END, f"{text}\n")
        else:
            self.results_text.insert(tk.END, f"❌ No verses found containing: '{query}'")

        self.results_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = BibleSearchApp()
    app.configure(bg='white')  # Set background white for better image visibility
    app.mainloop()
