# 🧠 Python Basic AI Desktop Application

- A sleek, user-friendly AI chatbot desktop app built with Python and CustomTkinter. 
- This assistant integrates multiple AI models like Gemini and Groq models.
- Supports TTS using Elevenlabs popular voices.
- Has modern looking GUI like buttons and chat displays. 
- Allows selecting desired AI models and AI voices.
- Simple Authentication system for using application and updating credentials.
- Stores the passwords and username in database (here MongoDB) safely rather than local file.
- saves chat conversations safely to database and can be deleted anytime.
---

## 📌 1. About the Project

- This project is developed for enhancing skills in python GUI and practicing it and not as production ready application. 
- This project is a workable desktop-based AI Application developed using Python's `CustomTkinter` for the GUI. It connects with different LLM APIs like `Google Gemini` and `Groq`.

_Note: didn't use paid LLM providers like `Claude` and `ChatGPT` as this project is intend to use free services only._

---

## ✨ 2. Features

✅ **Multi-model support**  
- Google Gemini (Pro & Flash)   
- Groq (Meta Llama, Gemma 2)
- select your desired models anytime from 7 total models (Gemini and Groq combined).
- Not only AI models, you can also change AI voices for TTS from total 4 voices (2 male, 2 female).
_Note: You can add more models from Gemini and Groq. For this project, it is limited to 7._

✅ **Streaming AI Responses**  
- Real-time chunk-wise response. (partially)
- Built using Gemini's `generate_content_stream()`

✅ **Dynamic Chat UI**  
- chat bubbles for user and AI text  
- Scrollable history with message alignment  

✅ **Model Selection Window**  
- Choose from multiple models via radio buttons  
- Choose Mutliple AI (Google and Groq) and TTS Voice Models (ElevenLabs) 

✅ **Voice Support (TTS)**  
- Uses ElevenLabs API to convert AI response to audio  
- "Speak" button shows **Speaking...** while audio is playing  
- Supports voice selection from 4 default ElevenLabs Voice models
- _Note : speak button takes longer time (approx 10 seconds maximun) for TTS during first use._

✅ **Keyboard Shortcuts**  
- `Enter` to send message  

✅ **User Settings**  
- User can update their display name on application.
- Also update password and username with verification before updating.
- delete Chat Historty if you want to.

✅ **Saves Chat History**
- Saves Chat conversations in database safely.
- View Chat History from app anytime with _History_ button.
- Can delete chat conversations permanently anytime through settings.

---

## 🛠️ 3. Modules Used

| Module         | Purpose                               |
|----------------|---------------------------------------|
| `customtkinter`| Modern, styled GUI toolkit            |
| `threading`    | Background processing (e.g., TTS/streaming) |
| `genai`        | Gemini API client                     |
| `groq`         | groq API                              |
| `tkmessagebox` | Popup alerts and feedback             |
| `elevenlabs`   | TTS audio generation                  |
| `os`, `re`     | Utility handling                      |
| `pymongo`      | MongoDB connection                    |

---

## 📁 4. Project Directory Structure
```
AI_Chat_Assistant/
│
├── main.py # Main application file
├── gitignore  # ignore .env file
├── README.md # You're reading it!
└── screenshots/ # UI screenshots for documentation
```
---

## 🧾 5. Conclusion

This project demonstrates a desktop chatbot powered by modern popular AI models and clean UI/UX practices. It blends real-time AI communication, voice capabilities, and multi-model flexibility into one responsive interface.

Built to mimic the responsiveness and intelligence of modern chat assistants, this project is ideal for:
- AI learners exploring LLM integrations
- Students building Python GUI apps
- Python students looking for AI + python GUI application

> 💡 Features you can add:
> - Integrate LangChain chat memory (MongoDB-backed)  
> - Add chatbot summarization & recall  
> - Implement "Stop Response" Speak button.

---

## Important Links:
1. https://ai.google.dev/gemini-api/docs
2. https://aistudio.google.com
3. https://console.groq.com/docs/quickstart
4. https://elevenlabs.io/app/home
5. https://elevenlabs.io/docs/quickstart
6. https://customtkinter.tomschimansky.com
