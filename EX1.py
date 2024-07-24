import tkinter as tk
from tkinter import scrolledtext, messagebox
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sqlite3

# إعداد مكتبة nltk
nltk.download('punkt')
nltk.download('stopwords')

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Simple Chatbot")
        self.root.configure(bg="#34495E")

        # الردود المبدئية
        self.responses = {
            "hello": "Hi there!",
            "how are you": "I'm just a computer program, but thanks for asking!",
            "bye": "Goodbye! Take care.",
            "default": "I'm sorry, I don't understand that."
        }

        # إعداد قاعدة البيانات
        self.conn = sqlite3.connect('learned_responses.db')
        self.create_table()

        # تحميل الردود المتعلمة من قاعدة البيانات
        self.learned_responses = self.load_learned_responses()

        # إعداد واجهة المستخدم
        self.setup_ui()

    def create_table(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS responses
                                (message TEXT PRIMARY KEY NOT NULL,
                                response TEXT NOT NULL);''')

    def setup_ui(self):
        # صندوق النص لعرض المحادثة
        self.chat_history = scrolledtext.ScrolledText(self.root, width=50, height=20, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 12), state="disabled")
        self.chat_history.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # التسمية وحقل الإدخال
        self.entry_label = tk.Label(self.root, text="Enter message:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12))
        self.entry_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.entry_field = tk.Entry(self.root, width=40, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 12))
        self.entry_field.grid(row=1, column=1, padx=10, pady=5)
        self.entry_field.bind("<Return>", self.send_message)

        # زر الإرسال
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message, bg="#3498DB", fg="#ECF0F1", font=("Arial", 10, "bold"))
        self.send_button.grid(row=1, column=2, pady=5)

        # زر التعلم
        self.learn_button = tk.Button(self.root, text="Learn", command=self.learn_message, bg="#E74C3C", fg="#ECF0F1", font=("Arial", 10, "bold"))
        self.learn_button.grid(row=2, column=2, pady=5)

    def send_message(self, event=None):
        user_input = self.entry_field.get()
        self.display_message(user_input, "You")
        self.entry_field.delete(0, tk.END)

        bot_response = self.get_chatbot_response(user_input)
        self.display_message(bot_response, "Chatbot")

    def display_message(self, message, sender):
        self.chat_history.configure(state="normal")
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.yview(tk.END)

    def preprocess_input(self, user_input):
        # تحليل النص
        tokens = word_tokenize(user_input.lower())
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [w for w in tokens if not w in stop_words]
        return ' '.join(filtered_tokens)

    def get_chatbot_response(self, user_input):
        preprocessed_input = self.preprocess_input(user_input)
        response = self.learned_responses.get(preprocessed_input)
        if response:
            return response
        return self.responses.get(preprocessed_input, self.responses["default"])

    def learn_message(self):
        learn_window = tk.Toplevel(self.root)
        learn_window.title("Learn")
        learn_window.configure(bg="#34495E")

        message_label = tk.Label(learn_window, text="Enter message to learn:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12))
        message_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        message_entry = tk.Entry(learn_window, width=40, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 12))
        message_entry.grid(row=0, column=1, padx=10, pady=5)

        response_label = tk.Label(learn_window, text="Enter expected response:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12))
        response_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        response_entry = tk.Entry(learn_window, width=40, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 12))
        response_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_learned_message():
            learned_message = message_entry.get().lower()
            expected_response = response_entry.get()
            if learned_message and expected_response:
                preprocessed_message = self.preprocess_input(learned_message)
                self.learned_responses[preprocessed_message] = expected_response
                self.save_learned_response_to_db(preprocessed_message, expected_response)
                messagebox.showinfo("Learn", "Message learned successfully!")
                learn_window.destroy()

        save_button = tk.Button(learn_window, text="Save", command=save_learned_message, bg="#27AE60", fg="#ECF0F1", font=("Arial", 10, "bold"))
        save_button.grid(row=2, columnspan=2, pady=10)

    def save_learned_response_to_db(self, message, response):
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO responses (message, response) VALUES (?, ?)", (message, response))

    def load_learned_responses(self):
        responses = {}
        with self.conn:
            cursor = self.conn.execute("SELECT message, response FROM responses")
            for row in cursor:
                responses[row[0]] = row[1]
        return responses

def main():
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
