import customtkinter as ctk
from tkinter import messagebox
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from dotenv import load_dotenv
from elevenlabs import ElevenLabs,play
import os
import random
from google import genai
from groq import Groq
import re
import threading
import queue
import datetime
from datetime import datetime
# --------------------------------------------------

# load data from .env file
load_dotenv()
# get MongoDB URI from .env file
mongo_uri= os.getenv('MONGO_URI')
# create client for database
client_db = MongoClient(mongo_uri)
# select database name and collection name
db = client_db['AIChat']
# collection for user's password and username
users_data_collection = db['users'] 
# collection for user's name
user_name_collection = db["user_name"]
# collection for AI history
AI_chat_collection = db["chat_history"]
# =====================================
# load elevenlabs API key from .env file
client_labs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)
# =====================================
# get APi Gemini API key from .env file
client_ai = genai.Client()
# ======================================
# get Groq API key
clinet_groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# --------------------------------------------------------------

# create a class for AI application
class myapp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x260')
        self.title('Login')
        self.grid_columnconfigure((0,1,2), weight=1)
        # ----------------- ---------------------------------------create login window widgets ----------------------------------------------------
        # heading
        ctk.CTkLabel(self, text='welcome to AI Talk', font=('Georgia',21,'italic'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10, columnspan=3)
        # frame holding username and password
        self.frame_1 = ctk.CTkFrame(self, width=500, height=220, fg_color='#A8F1FF', corner_radius=10)
        self.frame_1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        self.frame_1.grid_columnconfigure((0, 1, 2), weight=1) 
        # Username Label
        self.username_label = ctk.CTkLabel(self.frame_1, text='Username', text_color='Black', font=('Arial',13,'bold'))
        self.username_label.grid(row=0, column=0, padx=10,pady=10)
        # Password label
        self.pwd_label = ctk.CTkLabel(self.frame_1, text='Password', text_color='Black', font=('Arial',13,'bold'))
        self.pwd_label.grid(row=1, column=0, padx=10,pady=10)
        # Username entry
        self.username_entry = ctk.CTkEntry(self.frame_1, width=230, corner_radius=10)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        # password entry
        self.pwd_entry = ctk.CTkEntry(self.frame_1, width=230, corner_radius=10,show='*')
        self.pwd_entry.grid(row=1, column=1, padx=10, pady=10)
        # login button 
        ctk.CTkButton(self, text='Login', command=self.login, fg_color='#81E7AF', text_color='black', border_color='black', border_width=2, corner_radius=8, hover_color='#03A791',font=('Arial',13,'bold'), height=30, width=20).grid(row=2, column=2, padx=10, pady=10, sticky='ew')
        # clear button
        ctk.CTkButton(self, text='clear', command=self.clear, fg_color='#FFD66B', text_color='black', border_color='black', border_width=2, corner_radius=8, hover_color='#FFA62F',font=('Arial',13,'bold'), height=30, width=20).grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        # show password button
        self.show_pass_btn = ctk.CTkButton(self, text='show', command=self.toggle, fg_color='#4ED7F1', text_color='black', border_color='black', border_width=2, corner_radius=8, font=('Arial',13,'bold'), height=30, width=20)
        self.show_pass_btn.grid(row=2, column=1, padx=10, pady=10, sticky='ew')    
    
    # -------------------------------------------- functions for login, clear and show password buttons ----------------------------------------------------------------------
        
    # function to clear password and username
    def clear(self):
        self.username_entry.delete(0, ctk.END)
        self.pwd_entry.delete(0, ctk.END)
    # ------------------------------------------------------------------
    # function to toggle show and hide password
    def toggle(self):
        if self.pwd_entry.cget('show') == '*':
            self.pwd_entry.configure(show='')
            self.show_pass_btn.configure(text='Hide')
        else:
            self.pwd_entry.configure(show='*')
            self.show_pass_btn.configure(text='Show')
    # -------------------------------------------------------------------
    # function for login
    def login(self):
    # get user input from input fields
        username = self.username_entry.get()
        password = self.pwd_entry.get()
        try:
            user = users_data_collection.find_one({"username": username, "password": password})
            if user:
                messagebox.showinfo('info','login successful')
                self.username_entry.delete(0, ctk.END)
                self.pwd_entry.delete(0, ctk.END)
                # open password manager window
                self.dashboard()   # insert dashboard window here --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -- 
            elif username == '' and password == '':
                messagebox.showerror('Error','Enter Credentials to proceed')
            else:
                messagebox.showerror('Error','invalid credentials')
        except ConnectionFailure:
            messagebox("Eorror"," cannot connect to database")
        except ConnectionError:
            messagebox("Error","Connection Error!")

    # --------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------ DASBOARD WINDOW LOGIC ----------------------------------------------------------------

    # function consisting entire dashboard
    def dashboard(self):
        # withdraw login window
        self.withdraw()
        # create a new window
        root = ctk.CTkToplevel()
        root.geometry('900x710')
        root.title('Dashboard')
        # empty list that stores AI response : defined here to avoid UnboundLocalError
        response_text = [""]
        # default AI model
        current_model = ctk.StringVar(value="Gemini 2.5 Flash")
        # default voice for TTS
        TTS_model = ctk.StringVar(value='Mark')
        # -------------------------------------------------- ----Dashboard widgets --------------------------------------------------------------
        # fetching name of user from database
        user_name_data = user_name_collection.find_one()
        if user_name_data and "name" in user_name_data:
            name_of_user = user_name_data["name"]
        else:
            name_of_user = "friend"

        # ---------------------------------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------- FUNCTIONS FOR Dashboard BUTTONS ----------------------------------------------
        # srollable frame for AI response
        frame_2 = ctk.CTkScrollableFrame(root, width=600, height=400, corner_radius=8, border_width=2, border_color='#B13BFF')
        frame_2.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        # -------------------------------------------------------------------------------------------------------------------------------------
        # logout button logic
        def logout():
            root.destroy()
            self.deiconify()
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # function to clear user prompt
        def clear_prompt():
            user_input_entry.delete('1.0', ctk.END)
        # ----------------------------------------------------------------------------------------------------------------------------------------
        # function to clear AI generated text
        def clear_chat():
            for widget in frame_2.winfo_children():
                widget.destroy()
            # Reset message counter!
            message_row[0] = 0  

        # ----------------------------------------------------------------------------------------------------------------------------------------
        # function to close application
        def close():
            root.withdraw()
            self.deiconify()
            self.destroy()
        
        # ----------------------------------------------------------------------------------------------------------------------------------------
        # change model button logic (important)
        def change_model():
            root.withdraw()
            # create a new window
            win = ctk.CTkToplevel()
            win.geometry('230x270')
            win.title('Change AI Model')
            win.grid_columnconfigure(0, weight=1)
            # ------------------------------------------------ Change AI models Functions ----------------------------------------------------------------------------------
            # back button
            def back():
                win.destroy()
                root.deiconify()

            # ==================================================== New window for changing AI model =================================================================    
            def change_ai_model():
                # close previous window
                win.withdraw()
                # create new window
                ai = ctk.CTkToplevel()
                ai.title("change AI model")
                ai.geometry('400x350')
                # ------------------------------------------------------------
                # function to go back
                def cancel():
                    ai.destroy()
                    win.deiconify()
                # ------------------------------------------------------------ change AI model widgets -----------------------------------------------------------------
                # heading
                ctk.CTkLabel(ai, text='choose your desired AI model', font=('Georgia',16,'italic'), text_color='#D4F6FF').grid(row=0, column=0, padx=10, pady=10, columnspan=2)
                # frame for gemini models
                gemini_frames = ctk.CTkFrame(ai, width=200, height=170, corner_radius=8, fg_color='transparent', border_width=1, border_color='#B13BFF')
                gemini_frames.grid(row=1,column=0, padx=10, pady=10)
                # frame for Groq models
                groq_frames = ctk.CTkFrame(ai, width=200, height=200, corner_radius=8, fg_color='transparent', border_width=1, border_color='#B13BFF')
                groq_frames.grid(row=1,column=1, padx=10, pady=10)
                # heading for gemini
                ctk.CTkLabel(gemini_frames, text='Gemini', font=('Georgia',12,'bold'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10)
                # radio buttons for Gemini models
                # Gemini 2.5 Pro
                gR1 = ctk.CTkRadioButton(gemini_frames, text='Gemini 2.5 Pro', value='Gemini 2.5 Pro' ,font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','gemini-2.5-pro selected!'))
                gR1.grid(row=1, column=0, padx=10, pady=10, sticky='w')
                # Gemini 2.5 Flash
                gR2 = ctk.CTkRadioButton(gemini_frames, text='Gemini 2.5 Flash (default)', value='Gemini 2.5 Flash', font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','gemini-2.5-flash selected!'))
                gR2.grid(row=2, column=0, padx=10, pady=10, sticky='w')
                # gemini 2.0 flash
                gR3 = ctk.CTkRadioButton(gemini_frames, text='Gemini 2.0 Flash', value='Gemini 2.0 Flash' ,font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','gemini-2.0-flash selected!'))
                gR3.grid(row=3, column=0, padx=10, pady=10, sticky='w')
                # Gemini 2.0 Flash-Lite
                gR4 = ctk.CTkRadioButton(gemini_frames, text='Gemini 2.0 Flash-Lite', value='Gemini 2.0 Flash-Lite', font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','gemini-2.0-flash-lite selected!'))
                gR4.grid(row=4, column=0, padx=10, pady=10, sticky='w')
                # radio buttons for Groq models -  -  -  -  -  -  -  -  -  -  -
                # groq heading
                ctk.CTkLabel(groq_frames, text='Groq', font=('Georgia',12,'bold'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10)
                # llama guard-4
                xR1 = ctk.CTkRadioButton(groq_frames, text='meta-llama-guard-4-12b', value='meta-llama-guard-4-12b', font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','lllam-guard-4b selected!'))
                xR1.grid(row=1, column=0, padx=10, pady=10, sticky='w')
                # Gemma2 9b
                xR2 = ctk.CTkRadioButton(groq_frames, text='gemma2-9b-it', value='gemma2-9b-it', font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model)
                xR2.grid(row=2, column=0, padx=10, pady=10, sticky='w')
                # llama 3.1
                xR2 = ctk.CTkRadioButton(groq_frames, text='llama-3.1-8b-instant', value='llama-3.1-8b-instant', font=('Arial',10,'bold'), text_color='#A8F1FF', state='normal', variable=current_model, command=lambda: messagebox.showinfo('info','llama-3.1-8b selected!'))
                xR2.grid(row=3, column=0, padx=10, pady=10, sticky='w')
                # back button
                cancel_btn = ctk.CTkButton(ai, text='Back', command=cancel, font=('Arial',12,'bold'), text_color='black', fg_color='#FF6363', hover_color='#FF8282')
                cancel_btn.grid(row=2, column=0, padx=10, pady=10, sticky='ew', columnspan=2)
            # ============================================================== new window for voice change ========================================================
            def change_tts_model():
                win.withdraw()
                tts = ctk.CTkToplevel()
                tts.title('Change Voice')
                tts.geometry('350x275')
                # ------------------------------------------------------- functions for voice change window -----------------------------------------------------------
                def go_back():
                    tts.destroy()
                    win.deiconify()
                # --------------------------------------------------------- change voice widgets ----------------------------------------------------------------------
                # heading
                ctk.CTkLabel(tts, text='Select desired Audio Voice', font=('Georgia',16,'italic'), text_color='#A8F1FF').pack(pady=10)
                # radio button 1
                rad_1 = ctk.CTkRadioButton(tts, text='Mark (default)', value='Mark',corner_radius=1, text_color='#A8F1FF', state='normal', variable=TTS_model)
                rad_1.pack(pady=10)
                # radio button 2
                rad_2 = ctk.CTkRadioButton(tts, text='Antoni', value='Antoni',corner_radius=1, text_color='#A8F1FF', state='normal', variable=TTS_model)
                rad_2.pack(pady=10)
                # radio button 3
                rad_3 = ctk.CTkRadioButton(tts, text='Serena', value='Serena',corner_radius=1, text_color='#A8F1FF', state='normal', variable=TTS_model)
                rad_3.pack(pady=10)
                # radio button 3
                rad_4 = ctk.CTkRadioButton(tts, text='Domi', value='Domi',corner_radius=1, text_color='#A8F1FF', state='normal', variable=TTS_model)
                rad_4.pack(pady=10)
                # go back button (cancel)
                go_back_btn = ctk.CTkButton(tts, text='Back', command=go_back, fg_color='#F7374F', text_color='black', corner_radius=8, font=('Arial',14,'bold'), hover_color='#FF8282')
                go_back_btn.pack(pady=10)
            
            # -------------------------------------------------------------- Change model Widgets ---------------------------------------------------------
            # heading
            ctk.CTkLabel(win, text="TTS or AI model?", font=('Georgia',14,'italic'), text_color='#D4F6FF').grid(row=0, column=0, padx=10, pady=10)
            # change ai model button
            ai_btn = ctk.CTkButton(win, text='change AI model', command=change_ai_model, fg_color='#A8F1FF', text_color='black', corner_radius=8, font=('Arial',13,'bold'), hover_color='#E8F9FF', height=30)
            ai_btn.grid(row=1, column=0, padx=10, pady=10)
            # change Audio voice
            voice_btn = ctk.CTkButton(win, text='change audio voice', command=change_tts_model, fg_color='#A8F1FF', text_color='black', corner_radius=8, font=('Arial',13,'bold'), hover_color='#E8F9FF', height=30)
            voice_btn.grid(row=2, column=0, padx=10, pady=10)
            # back button
            back_btn = ctk.CTkButton(win, text='back', command=back, fg_color='#FF6363', text_color='black', border_color='black', border_width=2, corner_radius=8, font=('Arial',12,'bold'), hover_color='#FF8282', height=30)
            back_btn.grid(row=3, column=0, padx=10, pady=10)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------
        # list to count the row inside frame_2
        message_row=[0]

        # function to add messages into fram_2
        def add_message(sender, message_text):
            # determine the alignment of text according user or AI
            # if the sender is user (you)
            if sender == 'You':
                anchor_side = 'e'
                fg_color = '#A8F1FF'
            # otherwise sender is AI
            elif sender == "AI":
                anchor_side = 'w'
                fg_color = '#E1FFC7'
            # create a wrapper frame for this message
            message_frame = ctk.CTkFrame(frame_2, fg_color=fg_color, corner_radius=8, width=580)
            # insert message text as a label inside this frame (message_frame)
            message_label = ctk.CTkLabel(message_frame, text=message_text, font=('Arial',12,'bold'), text_color='black', fg_color='transparent', wraplength=580, anchor=anchor_side)
            message_label.pack(padx=5, pady=5, side='left')
            # place the message_frame inside frame_2
            message_frame.grid(row=message_row[0], column=0, sticky=anchor_side, padx=10, pady=5)
            # increment the row for the next message
            message_row[0] += 1
            # if sender is AI
            if sender.startswith("AI"):
                return message_label
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # function to produce streaming responses from Gemini and Groq models using thread and qeue
        def generate_response_threaded(prompt, q):
            """
            This function runs in a separate thread to avoid blocking the UI.
            It calls the selected AI model (Gemini or Groq) and puts the response 
            chunks into a queue.
            """
            # function to clean AI's output to plain text
            def clean_text(text):
                # Replace markdown-like bolding: **text** → text
                text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
                #  Replace markdown bullets: * text → • text
                text = re.sub(r"\n\s*\*\s+", "\n• ", text)
                # Replace inline asterisks with nothing (optional fallback)
                text = text.replace("*", "")
                return text
                
            try:
                selected_model = current_model.get()

                if selected_model.startswith("Gemini"):
                    model_name = selected_model.replace(" (defualt) ", "").lower().replace(" ", "-")
                    response_stream = client_ai.models.generate_content_stream(
                        model=model_name,
                        contents=prompt,
                    )
                    for chunk in response_stream:
                        q.put(chunk.text)

            # --- Groq Models ---
                else:
                    chat_completion_stream = clinet_groq.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=selected_model,
                        stream=True,  # Enable streaming for Groq
                    )
                    for chunk in chat_completion_stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            q.put(clean_text(content))

            except Exception as e:
                q.put(f"\n\nAn error occurred: {str(e)}")
            finally:
                # Put a sentinel value (None) to signal the end of the stream
                q.put(None)

            #----------------------------------------------------------------------------------------------------------------------------------
        def process_queue(q, ai_label):
            """
            This function runs in the main UI thread. It checks the queue for new
            text chunks from the worker thread and updates the AI response label.
            """
            try:
                # Process all chunks currently in the queue
                while not q.empty():
                    chunk = q.get_nowait()
                    if chunk is None:
                        # End of stream detected
                        send_btn.configure(state="normal") # Re-enable the send button
                        # Store the final, complete response for the 'Speak' function
                        response_text[0] = ai_label.cget("text")
                        # get data for database storage
                        chat = response_text[0]
                        prompt = user_input_entry.get('1.0',ctk.END).strip()
                        # create data in JSON
                        data = {"date":datetime.now(),"user":prompt,"AI":chat}
                        # store entry into database
                        AI_chat_collection.insert_one(data)
                        # reset the frame border color 
                        frame_2.configure(border_color = '#B13BFF')
                        return # Stop polling the queue
                    # Append the new chunk to the label
                    current_text = ai_label.cget("text")
                    ai_label.configure(text=current_text + chunk)
                    
                    # Auto-scroll to show the latest message
                    frame_2._parent_canvas.yview_moveto(1.0)


            except queue.Empty:
                # If the queue is empty, do nothing
                pass   
            # Schedule this function to run again after 100ms
            root.after(100, process_queue, q, ai_label)  

        # ----------------------------------------------------------------------------------------------------------------------------
        def send_prompt():
            """
            This function is called when the user clicks the 'Go' button.
            It sets up the thread and starts the AI response generation.
            """       

            prompt = user_input_entry.get('1.0', ctk.END).strip()
            if not prompt:
                messagebox.showerror('Error', 'Enter something!')
                return

            # Disable the send button to prevent multiple requests
            send_btn.configure(state="disabled")
            # change border color of frame_2 to red
            frame_2.configure(border_color = '#FF8282')
            # Display the user's prompt in the chat window
            add_message("You", prompt)
            # Create an empty placeholder label for the AI's streaming response
            ai_label = add_message('AI', '')
            # Clear the user input box
            #user_input_entry.delete('1.0', ctk.END)
            # Create a queue to communicate between threads
            response_queue = queue.Queue()
            # Create and start the worker thread
            thread = threading.Thread(target=generate_response_threaded, args=(prompt, response_queue))
            thread.daemon = True # Allows the main app to exit even if the thread is running
            thread.start()
            # Start the UI poller to update the chat window
            root.after(100, process_queue, response_queue, ai_label)  
        # --------------------------------------------------------------------------------------------------------------------------------------
        # function for TTS
        def speak():
            # text for speech (AI response)
            text_for_tts = response_text[0]
            if not text_for_tts:
                messagebox.showerror("Error","No text to speak!")
            else:
                selected_voice = TTS_model.get()

                # selecting voice id based on what voice user has chosen
                if selected_voice == 'Mark':
                    voice_id = 'UgBBYS2sOqTuMpoF3BR0'
                elif selected_voice == 'Serena':
                    voice_id = 'pMsXgVXv3BLzUgSXRplE'
                elif selected_voice == 'Antoni':
                    voice_id = 'ErXwobaYiN019PkySvjV'
                elif selected_voice == 'Domi':
                    voice_id = 'AZnzlk1XvdvUeBnXmlld'

                def tts_thread():
                    try:
                        # disable speaking button to avoid multiple clicks
                        speak_btn.configure(state=ctk.DISABLED)
                        # change button to speaking...
                        speak_btn.configure(text='speaking...', text_color='black')
                        speak_btn.update()
                        # TTS logic
                        audio = client_labs.text_to_speech.convert(
                            text=text_for_tts,
                            voice_id=voice_id,
                            model_id='eleven_multilingual_v2',
                            output_format='mp3_44100_128'
                        )
                        play(audio)
                        speak_btn.configure(state=ctk.NORMAL)
                    except Exception as e:
                        messagebox.showerror('Eror',f'{str(e)}')
                    finally:
                        # reset the button speaking
                        speak_btn.configure(text='Speak')
                # start threading            
                threading.Thread(target=tts_thread).start()
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        
        def view_history_window():
            root.withdraw()
            # ------------------------------------------------------- VIEW HISTORY WINDOW ---------------------------------------------------------------
            chat = ctk.CTkToplevel()
            chat.title("view history")
            chat.geometry("500x400")
            chat.grid_columnconfigure(0, weight=1)
            chat.grid_rowconfigure(0, weight=1)
            # ------------------------------------------------------ View history functions ---------------------------------------------------------
            def close():
                chat.destroy()
                root.deiconify()
            # ------------------------------------------------------ View history widgets --------------------------------------------------------------
            # scrollable window
            view_history_frame = ctk.CTkScrollableFrame(chat, width=450, height=300) 
            view_history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            # fech all data from database
            try:
                chat_history = list(AI_chat_collection.find().sort("date",-1))
            except Exception as e:
                messagebox.showerror(' database Error',f'failed to retrieve: {str(e)}')
                chat_history = []
            # if chat history is empty, show error
            if not chat_history:
                messagebox.showerror("Error","No data found!")
            else:
                for chat_entry in chat_history:
                    chat_time = chat_entry.get("date")
                    user_prompt = chat_entry.get("user","[No Prompt]")
                    ai_response = chat_entry.get("AI","[No response]")
                    # format datetime
                    if isinstance(chat_time, datetime):
                        formatted_date = chat_time.strftime("%Y-%m-%d-%H:%M:%S")
                    else:
                        formatted_date = "[Invalid date]"
                    # Create message block to store in a label
                    chat_text = f"Time: {formatted_date}\nYou: {name_of_user}: {user_prompt}\nAI: {ai_response}\n" #newline for spacing
                    # Create a frame for each chat entry to control padding and appearance
                    entry_frame = ctk.CTkFrame(view_history_frame, fg_color="transparent", corner_radius=8, border_width=1, border_color="#B13BFF")
                    entry_frame.pack(fill="x", padx=5, pady=5) # Fill horizontally
                    # message label that lies within the frame
                    message_label = ctk.CTkLabel(entry_frame, text=chat_text, font=('Arial',12), wraplength=420, text_color='#A8F1FF', justify="left") 
                    message_label.pack(pady=5, padx=5, anchor="w") # Anchor to west
            # Back button
            ctk.CTkButton(chat, text='Back', command=close, font=('Arial',12,'bold'), width=80, fg_color='#F7374F', hover_color='#FF8282', text_color='black').grid(row=1, column=0, pady=10)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------
        def settings():
            # close the previous window
            root.withdraw()
            # create a new window for settings
            control = ctk.CTkToplevel()
            control.title("Settings")
            control.geometry('250x250')
            control.grid_columnconfigure(0, weight=1)
            # ----------------------------------------------------------- Settings functions -----------------------------------------------------------------
            def back():
                control.destroy()
                root.deiconify()
            # -------------------------------------------------------------------
            # function to change the name of the user
            def change_name():
                # close the previous window
                control.withdraw()
                # ========================================================== Change name window ===============================================================
                # create a new window
                name = ctk.CTkToplevel()
                name.title('change name')
                name.geometry('350x200')
                # --------------------------------------------------------- Change name functions --------------------------------------------------------------
                # function to change name
                def change_name_logic():
                    # get current and new user name
                    current_name = current_name_entry.get().strip()
                    new_name = new_name_entry.get().strip()
                    if not current_name and not new_name:
                        messagebox.showerror("Error","Please fill the data!")
                    elif current_name != name_of_user:
                        messagebox.showerror('Error!',"Current name is incorrect!")
                    else:
                        # first delete the data from database
                        user_name_collection.delete_many({})
                        # insert new data into database
                        user_name_collection.insert_one({"name":new_name})
                        # notify the user
                        messagebox.showinfo('info',f"'{current_name}' has changed to '{new_name}'")
                        # clear the data
                        current_name_entry.delete(0, ctk.END)
                        new_name_entry.delete(0, ctk.END)
                # --------------------------------------------------------------------------------
                # function to go back
                def back():
                    name.destroy()
                    control.deiconify()            
                # --------------------------------------------------------- Change name widgets -----------------------------------------------------------------

                name_frame_1 = ctk.CTkFrame(name, width=320, height=160, border_color='#B13BFF', border_width=1, fg_color='transparent')
                name_frame_1.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
                # new name label 
                ctk.CTkLabel(name_frame_1, text='Current Name', font=('Arial',11,'bold'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10, sticky='w')
                # current name entry
                current_name_entry = ctk.CTkEntry(name_frame_1, font=('Arial',11), width=175)
                current_name_entry.grid(row=0, column=1, padx=10, pady=10)
                # new name label
                ctk.CTkLabel(name_frame_1, text='New Name', font=('Arial',11,'bold'), text_color='#A8F1FF').grid(row=1, column=0, padx=10, pady=10, sticky='w')
                # new name entry
                new_name_entry = ctk.CTkEntry(name_frame_1, font=('Arial',11), width=175)
                new_name_entry.grid(row=1, column=1, padx=10, pady=10)
                # back button
                ctk.CTkButton(name, text="Back", command=back, font=('Arial',10,'bold'), fg_color='#F7374F', hover_color='#FF8282', text_color='black', width=80).grid(row=1, column=0, padx=10, pady=10)
                # Confiem button
                ctk.CTkButton(name, text="Change", command=change_name_logic, font=('Arial',10,'bold'), fg_color='#03A791', hover_color='#81E7AF', text_color='black', width=80).grid(row=1, column=1, padx=10, pady=10)
            
        # =============================================================== change credentials window ==============================================================
            def change_credentials():
                # close the previous window
                control.withdraw()
                # create a new window
                verify = ctk.CTkToplevel()
                verify.title("chage credntials")
                verify.geometry("350x250")
                verify.grid_columnconfigure(0, weight=1)
                # -------------------------------------------------------------- Verifying user window functions ---------------------------------------------------
                # back button
                def back_btn_logic():
                    verify.destroy()
                    control.deiconify()

                # ======================================================== window to change credentials ==============================================================
                def change_credentials_window():
                    # close the previous window
                    verify.withdraw()
                    # create the new window
                    cred = ctk.CTkToplevel()
                    cred.geometry("400x300")
                    cred.title('change credentials')
                    cred.grid_columnconfigure((0,1), weight=1)
                    # ---------------------------------------------------------- change credentials functions ------------------------------------------------------
                    # back button
                    def go_back():
                        cred.destroy()
                        verify.deiconify()
                    # ------------------------------------------------------------------------
                    # change credentials logic
                    def change_credentials_loigc():
                        # get username and password
                        new_username = new_username_entry.get().strip()
                        new_pwd = new_pwd_entry.get().strip()
                        confirm_pwd = confirm_pwd_entry.get().strip()
                        # allow user only when confirm password is correct
                        if new_pwd == confirm_pwd:
                            # delete the data from database
                            users_data_collection.delete_many({})
                            # then insert new password and username
                            entry = {"username":new_username, "password":new_pwd}
                            users_data_collection.insert_one(entry)
                            messagebox.showinfo('info','credentials updated successfully!')
                            new_username_entry.delete(0, ctk.END)
                            new_pwd_entry.delete(0, ctk.END)
                            confirm_pwd_entry.delete(0, ctk.END)
                        elif new_pwd != confirm_pwd:
                            messagebox.showerror("Error","password didn't confirm! Check password")
                        elif not new_pwd and not confirm_pwd and not new_username:
                            messagebox.showerror('Error','Please fill the data.')

                    # --------------------------------------------------- change credentials widgets -----------------------------------------------------------------
                    # frame
                    cred_frame = ctk.CTkFrame(cred, width=360, height=250, fg_color='transparent', border_width=2, border_color='#B13BFF')
                    cred_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
                    # new username label
                    ctk.CTkLabel(cred_frame, text='New Username', font=('Arial',12,'bold'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10)
                    # New password
                    ctk.CTkLabel(cred_frame, text='New password', font=('Arial',12,'bold'), text_color='#A8F1FF').grid(row=1, column=0, padx=10, pady=10)
                    # confirm password
                    ctk.CTkLabel(cred_frame, text='Confirm password', font=('Arial',12,'bold'), text_color='#A8F1FF').grid(row=2, column=0, padx=10, pady=10)
                    # new username entry
                    new_username_entry = ctk.CTkEntry(cred_frame, width=150, text_color='#A8F1FF', font=('Arial',12))
                    new_username_entry.grid(row=0, column=1, padx=10, pady=10)
                    # new password entry
                    new_pwd_entry = ctk.CTkEntry(cred_frame, width=150, text_color='#A8F1FF', font=('Arial',11))
                    new_pwd_entry.grid(row=1, column=1, padx=10, pady=10)
                    # confirm password entry
                    confirm_pwd_entry = ctk.CTkEntry(cred_frame, width=150, text_color='#A8F1FF', font=('Arial',11))
                    confirm_pwd_entry.grid(row=2, column=1, padx=10, pady=10)
                    # back button
                    ctk.CTkButton(cred, text='Back', font=('Arial',10,'bold'), command=go_back, fg_color='#F7374F', hover=True, hover_color='#FF8282', width=80).grid(row=1, column=0, padx=10, pady=10)
                    # confirm button
                    ctk.CTkButton(cred, text='Confirm', font=('Arial',10,'bold'), command=change_credentials_loigc, text_color='black',fg_color='#4ED7F1', hover=True, hover_color='#A8F1FF', width=80).grid(row=1, column=1, padx=10, pady=10)
                # ------------------------------------------------------------------------------------------------------------------------------------------------------
                # verify logic function
                def verify_logic():
                    user_cred_data = users_data_collection.find_one()
                    user_pwd = user_cred_data["password"]
                    pwd = pwd_entry.get().strip()
                    if not pwd:
                        messagebox.showerror('Error','Enter password to proceed')
                    elif pwd == user_pwd:
                        messagebox.showinfo('info','User verified.')
                        pwd_entry.delete(0, ctk.END)
                        # open the credentials window after verifying the user
                        change_credentials_window()
                    else:
                        messagebox.showerror('Error','password is incorrect.')
                # -------------------------------------------------------------------------------------
                # -------------------------------------------------------- Verifying user window widgets --------------------------------------------------------------
                # heading
                ctk.CTkLabel(verify, text="verify it's you before you proceed", font=('Georgia',15,'italic'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10)
                # login frame
                verify_frame = ctk.CTkFrame(verify, width=300, height=230, fg_color='transparent', border_width=2, border_color='#B13BFF')
                verify_frame.grid(row=1, column=0, padx=10, pady=10)
                # password label
                ctk.CTkLabel(verify_frame, text="Password", font=('Georgia',12,'italic'), text_color='#A8F1FF').grid(row=0, column=0, padx=10, pady=10)
                # password entry
                pwd_entry = ctk.CTkEntry(verify_frame, width=160, font=('Arial',10,'bold'), text_color='#A8F1FF')
                pwd_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
                # verify button
                verify_btn = ctk.CTkButton(verify_frame, text='Veirfy', command=verify_logic, text_color='black',font=('Arial',10,'bold'), fg_color='#4ED7F1', hover_color='#A8F1FF', width=120)
                verify_btn.grid(row=1, column=1, padx=10, pady=10)
                # back button
                back_btn = ctk.CTkButton(verify_frame, text='Back', command=back_btn_logic,font=('Arial',10,'bold'), fg_color='#F7374F', hover_color='#FF8282', width=120)
                back_btn.grid(row=1, column=0, padx=10, pady=10)
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------
            # function to delete chat history
            def delete_chat_history():
                # close previous window
                control.withdraw()
                # create new window
                # ===================================================== confirm deletion window ======================================================================= 
                delete = ctk.CTkToplevel()
                delete.title("cofirm deletion")
                delete.geometry("200x150")
                # ==================================================== confirm deletion functions ===================================================================
                # no button (back)
                def no_btn():
                    delete.destroy()
                    control.deiconify()
                # ----------------------------------------------------------------------------------------------------------------------------------------------------
                # confirm deletion logc
                def confirm_del():
                    data = AI_chat_collection.find_one()
                    if not data:
                        messagebox.showerror('Error',"No chat history to delete.")
                    else:
                        AI_chat_collection.delete_many({})
                        messagebox.showinfo("info","chat history deleted successfully")
                        delete.destroy()
                        control.deiconify()

                # ==================================================== confirm deletion widgets =====================================================================
                # heading
                ctk.CTkLabel(delete, text='Confirm deleteion?', font=('arial',16,'italic'), text_color='#A8F1FF').pack(pady=10)
                # frame to hold NO and YES button
                frame_7 = ctk.CTkFrame(delete, width=190, height=140, corner_radius=8)
                frame_7.pack(pady=10)
                # confirm deletion button
                ctk.CTkButton(frame_7, text="Yes", command=confirm_del, fg_color='#FF8282', hover_color='#FFDCDC', font=('arial',14,'bold'), text_color='black', width=75, height=120).pack(pady=10, padx=10,side='left')
                # back button
                ctk.CTkButton(frame_7, text="No", command=no_btn, fg_color='#81E7AF', hover_color='#EBFFD8', font=('arial',14,'bold'), text_color='black', width=75, height=120).pack(pady=10, padx=10,side='right')

    # ------------------------------------------------------------------ Settings widgets ---------------------------------------------------------------------
            # heading
            ctk.CTkLabel(control, text='Change Settings', text_color='#A8F1FF', font=('Georgia',15,'italic')).grid(row=0, column=0, padx=10, pady=10)
            # change name button
            change_name_btn = ctk.CTkButton(control, text="change name", command=change_name, font=('Arial',12,'bold'), fg_color='#63C8FF', hover_color='#A8F1FF' ,text_color='black')
            change_name_btn.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
            # change credentials button
            change_pwd_btn = ctk.CTkButton(control, text="change credentials", command=change_credentials, font=('Arial',12,'bold'), fg_color='#63C8FF', hover_color='#A8F1FF' ,text_color='black')
            change_pwd_btn.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
            # delete chat history
            ctk.CTkButton(control, text='Delete Chat History', command=delete_chat_history, font=("arial",12,'bold'), fg_color="#63C8FF", hover_color='#A8F1FF', text_color='black').grid(row=3, column=0, padx=10, pady=10, sticky='ew')
            # back button
            ctk.CTkButton(control, text="Back", command=back, font=('Arial',10,'bold'), fg_color='#F7374F', hover_color='#FF8282', text_color='white', width=50).grid(row=4, column=0, padx=10, pady=20)

        # ------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------ DASHBOARD WIDGETS -----------------------------------------------------------------------------
        # creating message list which stores various welcome messages
        message_list = [f'Hello, {name_of_user}',
                        f'Welcome {name_of_user}!',
                        f'{name_of_user}, how may I help you today?',
                        f"what's on your mind today {name_of_user}?",
                        f"let's get started {name_of_user}!",
                        f'Hola...']
        message = random.choice(message_list)
        # welcome message
        ctk.CTkLabel(root, text=message, font=('Georgia',21,'italic'), text_color="#A8F1FF").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        # fame to hold user input field and send button
        frame_3 = ctk.CTkFrame(root, width=600, height=100, fg_color='transparent')
        frame_3.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        frame_3.grid_columnconfigure((0,1), weight=1)
        # scrollable user input field
        user_input_entry = ctk.CTkTextbox(frame_3, width=550, height=100, text_color='white', font=('Arial',14), corner_radius=8, border_width=2, border_color='#B13BFF')
        user_input_entry.pack(side='left',padx=5, pady=30)
        # send button
        send_btn = ctk.CTkButton(frame_3, text='Go', command=send_prompt, fg_color='#4DFFBE', text_color='black', border_width=2, corner_radius=8, font=('Arial',14,'bold'), width=60, height=100, hover_color='#CFFFE2')
        send_btn.pack(side='right')
        # allow user to hit enter button to send prompt
        root.bind("<Return>", lambda event: send_prompt())
        # frame to hold logout and settings button
        frame_4 = ctk.CTkFrame(root, width=400, height=800, fg_color='transparent', corner_radius=8, border_width=1, border_color='#B13BFF')
        frame_4.grid(row=1, column=2, padx=10, pady=10)
        # logout button
        logout_btn = ctk.CTkButton(frame_4, text='Logout', command=logout, fg_color='#FF6500', text_color='white', hover_color='#FF8282', corner_radius=8,font=('Georgia',15,'bold'), height=50)        
        logout_btn.grid(row=0, column=0, padx=10,pady=10)
        # settings button
        settings_btn = ctk.CTkButton(frame_4, text='Settings', command=settings, fg_color='white', hover_color='#F5EFFF', corner_radius=8,font=('Georgia',15,'bold'), height=50, text_color='black')        
        settings_btn.grid(row=1, column=0, padx=10,pady=10)
        # speak button
        speak_btn = ctk.CTkButton(frame_4, text='Speak', command=speak, fg_color='#42C2FF',hover_color="#A8F1FF", corner_radius=8,font=('Georgia',15,'bold'), height=50, text_color='black')        
        speak_btn.grid(row=5, column=0, padx=10,pady=10)
        # view history button
        view_history_btn = ctk.CTkButton(frame_4, text='History', command=view_history_window, fg_color='#4DFFBE', hover_color="#CFFFE2", corner_radius=8,font=('Georgia',15,'bold'), height=50, text_color='black')   
        view_history_btn.grid(row=2, column=0, padx=10,pady=10)
        # frame to change model button
        frame_5 = ctk.CTkFrame(root, width=200, height=100, fg_color='transparent', corner_radius=8, border_color='#B13BFF', border_width=1)
        frame_5.grid(row=2, column=2, padx=10, pady=10)
        # change model button
        model_btn = ctk.CTkButton(frame_4, text='change Model', command=change_model, fg_color='#FFCC00', hover_color="#FFFA8D", corner_radius=8,font=('Georgia',15,'bold'), height=50, text_color='black')        
        model_btn.grid(row=4, column=0, padx=10,pady=10)
        # frame to hold the close button 
        frame_6 = ctk.CTkFrame(root, width=200, height=60, fg_color='transparent', corner_radius=8, border_color='#B13BFF', border_width=1)
        frame_6.grid(row=0, column=2, padx=10, pady=10)
        # clear chat button
        clear_chat_btn = ctk.CTkButton(frame_5, text='clear chat', command=clear_chat, fg_color='#FF6B6B', hover_color='#FFDCDC', corner_radius=8,font=('Georgia',14,'bold'), height=37, text_color='black')        
        clear_chat_btn.grid(row=1, column=0, padx=10,pady=5)
        # clear prompt button
        clear_prompt_btn = ctk.CTkButton(frame_5, text='clear prompt', command=clear_prompt, fg_color='#FFFA8D', hover_color='#FFD09B', corner_radius=8,font=('Georgia',14,'bold'), height=37, text_color='black')        
        clear_prompt_btn.grid(row=0, column=0, padx=10,pady=5)
        # close application button
        close_btn = ctk.CTkButton(frame_6, text='Close', command=close, fg_color='#C62300', hover_color="#FF8282", corner_radius=8,font=('Georgia',13,'bold'), height=30, text_color='white')        
        close_btn.grid(row=0, column=0, padx=10,pady=10)
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# run the app
app = myapp()
app.mainloop()