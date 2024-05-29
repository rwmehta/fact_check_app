import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os
import fitz
from docx import Document

class FactCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fact Checker App")

        self.frame = ttk.Frame(root, padding="10 10 10 10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.setup_main_interface()

    def setup_main_interface(self):
        # Clear the frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Label to guide the user
        label = ttk.Label(self.frame, text="Select the type of file to upload:")
        label.pack(pady=10)

        # Buttons for different file types
        ttk.Button(self.frame, text="Upload Video", command=lambda: self.upload_file('video')).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(self.frame, text="Upload Audio", command=lambda: self.upload_file('audio')).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(self.frame, text="Upload Text", command=lambda: self.upload_file('text')).pack(fill=tk.X, padx=5, pady=5)

    def upload_file(self, file_type):
        file_options = {
            'video': ('Video Files', '*.mp4 *.avi *.mov'),
            'audio': ('Audio Files', '*.mp3 *.wav *.aac'),
            'text': ('Text Files', '*.txt *.docx *.pdf')
        }
        file_type_description, file_extensions = file_options[file_type]
        file_path = filedialog.askopenfilename(title=f"Select {file_type_description}", filetypes=[(file_type_description, file_extensions)])
        
        if file_path:
            self.show_loading_screen()
            # Process the file in a separate thread
            Thread(target=self.process_file, args=(file_path, file_type)).start()
        else:
            messagebox.showinfo("File Load Canceled", "No file was selected.")

    def show_loading_screen(self):
        # Clear the frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Display loading message
        loading_label = ttk.Label(self.frame, text="Processing the file, please wait...")
        loading_label.pack(pady=20)

    def process_file(self, file_path, type):
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            
            if type == 'video':
                video_clip = VideoFileClip(file_path)
                audio_clip = video_clip.audio
                audio_file_path = os.path.join(temp_dir, "extracted_audio.wav")
                audio_clip.write_audiofile(audio_file_path)
                text = self.extract_text_from_audio(audio_file_path)
                audio_clip.close()
                video_clip.close()
            elif type == 'audio':
                text = self.extract_text_from_audio(file_path)
            else:
                text = self.read_text_file(file_path)

            # You can now use the extracted text for further processing
            self.extracted_text = text  # Store the text for use in the GUI

        except Exception as e:
            self.extracted_text = "An error occurred during file processing: " + str(e)

        # for filename in os.listdir(temp_dir):
        #     os.remove(os.path.join(temp_dir, filename))
        # os.rmdir(temp_dir)
        self.file_processing_done()

    def extract_text_from_audio(self, audio_file_path):
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            try:
                # Attempt to recognize speech using Google's free web service
                return recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                return f"Could not request results from Google Speech Recognition service; {e}"

    def read_text_file(self, file_path):
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            elif file_extension == 'docx':
                document = Document(file_path)
                return '\n'.join([paragraph.text for paragraph in document.paragraphs])
            
            elif file_extension == 'pdf':
                doc = fitz.open(file_path)
                text = ''
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text

        except Exception as e:
            return f"Failed to read file: {str(e)}"

    def file_processing_done(self):
        # Update GUI elements on the main thread
        self.root.after(0, self.show_results)

    def show_results(self):
        # Clear the frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Display processing complete message
        ttk.Label(self.frame, text="File processing complete!").pack(pady=20)

        # Create a text widget to display the extracted text
        text_widget = tk.Text(self.frame, height=15, width=50)
        text_widget.pack(pady=10, padx=10)
        text_widget.insert(tk.END, self.extracted_text)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

        # Scrollbar for the text widget
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)

        ttk.Button(self.frame, text="Back to main", command=self.setup_main_interface).pack(pady=20)

# Create the main window
root = tk.Tk()
app = FactCheckerApp(root)

# Start the application
root.mainloop()
