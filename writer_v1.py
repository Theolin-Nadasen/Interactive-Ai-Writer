import tkinter as tk
from tkinter import scrolledtext
import threading

from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM

from tts import talk

# 1. THE PROMPT TEMPLATE IS THE BIGGEST CHANGE
# We are no longer treating this as a chat. We are giving the AI a single block of text
# and asking it to continue it.
prompt_template = PromptTemplate.from_template(
    """You are a creative and collaborative writing partner.
Here is the text we have written together so far.
During your turn your task is to add the next part of the story or idea.

Continue the text in a natural and interesting way.
Write only 2-5 lines of text every turn.
Do not repeat the text I have given you. Only write your new addition.

---
Existing Text:
{current_text}
---

Your Addition:"""
)

# 2. THE LLM AND CHAIN SETUP
# The LLM setup is the same. The chain now uses our new prompt.
try:
    llm = OllamaLLM(model="gemma3n:e2b") # Using a smaller model like gemma2:2b can be faster for GUI apps
    # llm = OllamaLLM(model="gemma3n:e2b") # Your original model is fine too!
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
        self.root.geometry("800x600")

        # Main text area where user and AI write
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Once upon a time, in a world made of glass and whispers...")

        # Button to trigger the AI
        self.generate_button = tk.Button(root, text="AI, Continue the Story", command=self.trigger_ai_addition, font=("Arial", 12, "bold"))
        self.generate_button.pack(pady=10)

    def trigger_ai_addition(self):
        """
        This function is called when the button is pressed.
        It starts a new thread to run the AI generation to keep the GUI responsive.
        """
        # Disable the button to prevent multiple clicks while running
        self.generate_button.config(state=tk.DISABLED, text="AI is thinking...")
        
        # Run the potentially long-running AI call in a separate thread
        thread = threading.Thread(target=self.get_ai_addition)
        thread.start()

    def get_ai_addition(self):
        """
        This function handles the logic of getting text and calling the LangChain chain.
        """
        # 3. GETTING CONTEXT FROM THE GUI
        # We get the ENTIRE text from the widget.
        current_text = self.text_area.get("1.0", tk.END)

        # 4. INVOKING THE CHAIN WITH THE FULL TEXT
        # We invoke the chain with the single string of current_text.
        try:
            ai_response = self.chain.invoke({"current_text": current_text})

            # Schedule the GUI update to run on the main thread
            self.root.after(0, self.update_text_area, ai_response)
            
            talk(ai_response)
        
        except Exception as e:
            error_message = f"\n\n--- ERROR ---\nCould not get response from AI: {e}\n"
            self.root.after(0, self.update_text_area, error_message)
        finally:
            # Schedule the button re-enabling to run on the main thread
            self.root.after(0, self.enable_button)

    def update_text_area(self, new_text):
        """
        Appends the AI's response to the text area.
        This must be run from the main thread, which `root.after` ensures.
        """
        self.text_area.insert(tk.END, "\n\n" + new_text)
        self.text_area.see(tk.END) # Auto-scroll to the bottom

    def enable_button(self):
        """
        Re-enables the generate button.
        """
        self.generate_button.config(state=tk.NORMAL, text="AI, Continue the Story")


if __name__ == "__main__":
    # Standard Tkinter setup
    root = tk.Tk()
    app = CollaborativeWriterApp(root, chain)
    root.mainloop()