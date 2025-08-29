import tkinter as tk
from tkinter import scrolledtext, Label, Frame, filedialog, Listbox
from tkinter import ttk  # Import ttk for Combobox
import threading
import os

from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM

from tts import talk

# --- Dark Theme Color Palette ---
BG_COLOR = "#212121"
TEXT_COLOR = "#EAEAEA"
INPUT_BG_COLOR = "#3c3c3c"
BUTTON_BG_COLOR = "#4f4f4f"
CURSOR_COLOR = "white"
LISTBOX_BG_COLOR = "#3c3c3c"

# --- Prompt Template ---
prompt_template = PromptTemplate(
    input_variables=["personality", "current_text"],
    template="""You are a helpful AI assistant. Your current personality is: 
    ---Start of personality---
    {personality}
    ---End of personality---

Based on this role, your task is to seamlessly continue the text provided by the user.
Do not start a new paragraph. Do not add any introductory phrases.
Your response should flow perfectly from the user's last word, embodying the specified personality.

Do not use * as emphasis in response as the tool can not handle it.
---
User's Text:
{current_text}
---

Your Addition:"""
)

# --- Language Model Initialization ---
try:
    llm = OllamaLLM(model="gemma3n:e2b")
except Exception as e:
    print(f"Error initializing Ollama. Make sure Ollama is running.")
    print(f"Details: {e}")
    exit()

chain = prompt_template | llm

# --- Personality Management Window ---
class PersonalityWindow(tk.Toplevel):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("Manage Personalities")
        self.geometry("700x500")
        self.configure(bg=BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Widgets ---
        main_frame = Frame(self, bg=BG_COLOR)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Left side: List of personalities
        list_frame = Frame(main_frame, bg=BG_COLOR)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        list_label = Label(list_frame, text="Personalities", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        list_label.pack(pady=(0, 5))

        self.personality_listbox = Listbox(list_frame, bg=LISTBOX_BG_COLOR, fg=TEXT_COLOR, selectbackground=BUTTON_BG_COLOR, relief=tk.FLAT, borderwidth=0, highlightthickness=0)
        self.personality_listbox.pack(fill=tk.Y, expand=True)
        self.personality_listbox.bind("<<ListboxSelect>>", self.on_personality_select)

        # Right side: Text area for editing
        self.personality_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 12), bg=INPUT_BG_COLOR, fg=TEXT_COLOR, insertbackground=CURSOR_COLOR, relief=tk.FLAT, bd=10)
        self.personality_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bottom: Buttons
        button_frame = Frame(self, bg=BG_COLOR)
        button_frame.pack(pady=5, fill=tk.X, padx=10, side=tk.BOTTOM)

        self.load_folder_button = tk.Button(button_frame, text="Load Folder", command=self.load_folder, font=("Arial", 10, "bold"), bg=BUTTON_BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT)
        self.load_folder_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_personality, font=("Arial", 10, "bold"), bg=BUTTON_BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.update_listbox()

    def update_listbox(self):
        self.personality_listbox.delete(0, tk.END)
        for name in self.app.personalities.keys():
            self.personality_listbox.insert(tk.END, name)

    def on_personality_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            name = event.widget.get(index)
            self.personality_text.delete("1.0", tk.END)
            self.personality_text.insert(tk.END, self.app.personalities.get(name, ""))

    def load_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Personalities")
        if folder_path:
            self.app.load_personalities_from_folder(folder_path)
            self.update_listbox()

    def save_personality(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], title="Save Personality")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.personality_text.get("1.0", tk.END))
            # Add to personalities and update listbox
            name = os.path.basename(file_path).replace(".txt", "")
            self.app.personalities[name] = self.personality_text.get("1.0", tk.END)
            self.update_listbox()
            self.app.update_personality_dropdown()

    def on_close(self):
        self.app.personality_window = None
        self.destroy()

# --- Main Application Window ---
class CollaborativeWriterApp:
    def __init__(self, root, chain):
        self.root = root
        self.chain = chain
        self.root.title("AI Collaborative Writer")
        self.root.geometry("800x650")
        self.root.configure(bg=BG_COLOR)

        self.personalities = {"Default": "An expert creative writing assistant"}
        self.current_personality_name = tk.StringVar(value="Default")
        self.personality_window = None

        # --- Widgets ---
        personality_frame = Frame(root, bg=BG_COLOR)
        personality_frame.pack(pady=(10, 5), padx=10, fill=tk.X)

        personality_label = Label(personality_frame, text="AI Personality:", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        personality_label.pack(side=tk.LEFT, padx=(0, 5))

        self.personality_dropdown = ttk.Combobox(personality_frame, textvariable=self.current_personality_name, font=("Arial", 10), state="readonly")
        self.personality_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.update_personality_dropdown()

        self.manage_button = tk.Button(personality_frame, text="Manage", command=self.open_personality_window, font=("Arial", 10, "bold"), bg=BUTTON_BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT)
        self.manage_button.pack(side=tk.RIGHT, padx=5)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), bg=INPUT_BG_COLOR, fg=TEXT_COLOR, insertbackground=CURSOR_COLOR, relief=tk.FLAT, bd=10)
        self.text_area.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "The old sailor looked at the map and said")

        self.generate_button = tk.Button(root, text="AI, Continue", command=self.trigger_ai_addition, font=("Arial", 12, "bold"), bg=BUTTON_BG_COLOR, fg=TEXT_COLOR, activebackground="#6a6a6a", activeforeground=TEXT_COLOR, relief=tk.FLAT, bd=0)
        self.generate_button.pack(pady=10)

    def update_personality_dropdown(self):
        self.personality_dropdown['values'] = list(self.personalities.keys())

    def load_personalities_from_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                name = filename.replace(".txt", "")
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    self.personalities[name] = f.read().strip()
        self.update_personality_dropdown()

    def open_personality_window(self):
        if self.personality_window is None:
            self.personality_window = PersonalityWindow(self.root, self)
        else:
            self.personality_window.lift()

    def trigger_ai_addition(self):
        self.generate_button.config(state=tk.DISABLED, text="AI is thinking...")
        thread = threading.Thread(target=self.get_ai_addition)
        thread.start()

    def get_ai_addition(self):
        current_text = self.text_area.get("1.0", tk.END)
        personality_name = self.current_personality_name.get()
        personality_to_use = self.personalities.get(personality_name, "")
        
        try:
            ai_response = self.chain.invoke({
                "personality": personality_to_use,
                "current_text": current_text
            })
            
            self.root.after(0, self.update_text_area, ai_response)
            talk(ai_response)
        
        except Exception as e:
            error_message = f"\n\n--- ERROR ---\nCould not get response from AI: {e}\n"
            self.root.after(0, self.update_text_area, error_message)
        finally:
            self.root.after(0, self.enable_button)

    def update_text_area(self, new_text):
        self.text_area.insert(tk.END, " " + new_text.strip())
        self.text_area.see(tk.END)

    def enable_button(self):
        self.generate_button.config(state=tk.NORMAL, text="AI, Continue")


if __name__ == "__main__":
    root = tk.Tk()
    app = CollaborativeWriterApp(root, chain)
    root.mainloop()