import tkinter as tk
from tkinter import scrolledtext, Entry, Label, Frame
import threading

from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM

from tts import talk

# ### CHANGE 1: UPDATE THE PROMPT TEMPLATE ###
# It now takes a 'personality' variable. The instructions are more general,
# relying on the personality to guide the AI's style.
prompt_template = PromptTemplate(
    input_variables=["personality", "current_text"],
    template="""You are a helpful AI assistant. Your current personality is: {personality}

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

try:
    llm = OllamaLLM(model="gemma3n:e2b")
except Exception as e:
    print(f"Error initializing Ollama. Make sure Ollama is running.")
    print(f"Details: {e}")
    exit()

chain = prompt_template | llm

# --- Tkinter GUI Application ---

class CollaborativeWriterApp:
    def __init__(self, root, chain):
        self.root = root
        self.chain = chain
        self.root.title("AI Collaborative Writer")
        self.root.geometry("800x650") # Made the window a bit taller

        # ### CHANGE 2: ADD GUI WIDGETS FOR PERSONALITY INPUT ###
        # We use a Frame to group the label and entry box together neatly.
        personality_frame = Frame(root)
        personality_frame.pack(pady=(10, 5), padx=10, fill=tk.X)

        personality_label = Label(personality_frame, text="AI Personality:", font=("Arial", 10, "bold"))
        personality_label.pack(side=tk.LEFT, padx=(0, 5))

        self.personality_entry = Entry(personality_frame, font=("Arial", 10))
        self.personality_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # You can pre-fill it with a placeholder if you like
        self.personality_entry.insert(0, "An expert creative writing assistant")
        # --------------------------------------------------------------------

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "The old sailor looked at the map and said")

        self.generate_button = tk.Button(root, text="AI, Continue", command=self.trigger_ai_addition, font=("Arial", 12, "bold"))
        self.generate_button.pack(pady=10)
        
        # This will be our default if the user deletes the text in the entry box
        self.default_personality = "an expert creative writing assistant acting as an autocomplete tool"

    def trigger_ai_addition(self):
        self.generate_button.config(state=tk.DISABLED, text="AI is thinking...")
        thread = threading.Thread(target=self.get_ai_addition)
        thread.start()

    def get_ai_addition(self):
        # ### CHANGE 3: GET PERSONALITY AND INVOKE CHAIN WITH BOTH VARIABLES ###
        # Get the text from the main text area
        current_text = self.text_area.get("1.0", tk.END)
        
        # Get the personality from the entry box
        user_defined_personality = self.personality_entry.get().strip()
        
        # If the user cleared the box, use the default. Otherwise, use what they typed.
        personality_to_use = user_defined_personality or self.default_personality
        
        try:
            # Pass BOTH variables into the chain's invoke method
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
        # ---------------------------------------------------------------------

    def update_text_area(self, new_text):
        self.text_area.insert(tk.END, " " + new_text.strip())
        self.text_area.see(tk.END)

    def enable_button(self):
        self.generate_button.config(state=tk.NORMAL, text="AI, Continue")


if __name__ == "__main__":
    root = tk.Tk()
    app = CollaborativeWriterApp(root, chain)
    root.mainloop()