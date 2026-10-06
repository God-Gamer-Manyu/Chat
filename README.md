# Intelli Chat 💬

**Intelli Chat** is a standalone desktop chat application built in Python. It has two modes:

- **Chat with Friends:** real-time messaging (public broadcast or private) and image sharing between users over a TCP socket server, with **RSA-encrypted** traffic.
- **Chat with AI:** a conversational assistant powered by the OpenAI API that keeps conversation history across turns.

The GUI is built with **CustomTkinter**, with a dark theme, chat bubbles, profile pictures, timestamps and sound effects.

---

## ✨ Features

- 🔐 **User accounts:** sign-up and login backed by a **MySQL** database
- 👥 **Multi-client chat room:** live list of online users, public and private messages, join notifications
- 🖼️ **Image sharing:** send pictures that open in an in-app viewer
- 🤖 **AI assistant:** context-aware replies built from the conversation history
- 🔒 **Encryption:** RSA (1024-bit) for messages in transit and **Fernet** (symmetric) for locally stored conversations and credentials
- 🔊 **Sound effects** for send, receive and user-join events (via `pydub`)
- 🪵 **Built-in debug console:** every `print` is captured into a toggleable in-app log window

---

## 🏗️ Architecture & Concepts

```
              ┌──────────────────────── Client (Main.py) ───────────────────────┐
              │  CustomTkinter GUI  ──►  Login / Sign-up  ──►  DatabaseHandler   │──► MySQL (User table)
              │        │                                                         │
              │        ├──► aichat.py ──► OpenAI Completions API                 │
              │        └──► Client.py ──► TCP socket (RSA-encrypted) ────────────┼──► Server.py (ChatRoom)
              │  Utility.py: sounds · fonts · asset paths · log console          │        │
              └──────────────────────────────────────────────────────────────────┘        └──► broadcasts / routes to other clients
```

| Module | Responsibility |
|---|---|
| `Main.py` | App entry point and home screen (choose **AI** or **Friends**); handles login, profile picture, encrypted persistence of chat history |
| `Client.py` | Friends chat window; socket client; RSA key exchange; message chunking; image send/receive; per-user chat bubbles |
| `Server.py` | Multi-threaded TCP **chat room server** (`localhost:8888`): tracks clients and their public keys, routes private messages, broadcasts public ones, relays profile pictures |
| `aichat.py` | AI chat window; builds a prompt from history and calls OpenAI |
| `DatabaseHandler.py` | MySQL access via `PyMySQL` (add / check / delete users) |
| `Utility.py` | Shared constants (fonts, images, sounds), `%APPDATA%` storage paths, sound manager, log console |

**Key concepts:** client–server architecture · TCP sockets · multithreading · asymmetric (RSA) and symmetric (Fernet) encryption · message chunking and framing (`<END>` markers, `pickle` serialisation for files) · SQL (MySQL) · event-driven GUI programming · LLM API integration

---

## ⚙️ Getting Started

### Prerequisites
- **Windows** (the app stores data under `%APPDATA%\Intelli Chat` and uses `.ico` window icons)
- **Python 3.10+**
- **MySQL Server**, plus **FFmpeg** (required by `pydub` for audio playback)
- An **OpenAI API key** (for AI mode)

### 1. Clone & install dependencies

```bash
git clone https://github.com/God-Gamer-Manyu/Chat.git
cd Chat
python -m venv .venv
.venv\Scripts\activate
pip install customtkinter CTkListbox pillow cryptography rsa pymysql pydub "openai<1.0"
```

> `aichat.py` uses the legacy `openai.Completion` interface, so it needs `openai<1.0`.

### 2. Set up the database

```sql
CREATE DATABASE Chat;
USE Chat;
CREATE TABLE User (name VARCHAR(50) NOT NULL PRIMARY KEY, pass VARCHAR(50) NOT NULL);
```

Set the database credentials as environment variables (read by `DatabaseHandler.py`):

```bash
set CHAT_DB_USER=your_mysql_user          # macOS/Linux: export CHAT_DB_USER=...
set CHAT_DB_PASSWORD=your_mysql_password
```

### 3. Configure the AI key

`aichat.py` reads the key from the `OPENAI_API_KEY` environment variable:

```bash
set OPENAI_API_KEY=sk-...                 # macOS/Linux: export OPENAI_API_KEY=...
```

### 4. Run

```bash
# Terminal 1: start the chat server
python Server.py

# Terminal 2 (and more, one per user): start a client
python Main.py
```

Click **AI** to chat with the assistant, or **FRIENDS** to log in and join the chat room.

---

## 📁 Project Structure

```
Chat/
├── Main.py               # Entry point / home screen
├── Client.py             # Friends chat client + GUI
├── Server.py             # Socket chat-room server
├── aichat.py             # AI chat window
├── DatabaseHandler.py    # MySQL user store
├── Utility.py            # Shared helpers, assets, log console
├── Resources/            # Images, sound effects, Fernet key
└── server_profile_pic/   # Profile pictures received from other clients
```

## ⚠️ Notes

- This is a learning prototype. Passwords are stored in plain text in MySQL, and the server binds to `localhost` by default (change `HOST` in `Main.py`, `Client.py` and `Server.py` for LAN use).
- The `text-davinci-003` model used for AI chat has been retired by OpenAI. To make AI mode work today, switch to a current model through the Chat Completions API.

## 🛠️ Tech Stack

`Python` · `CustomTkinter` · `Sockets` · `Threading` · `RSA` · `Fernet (cryptography)` · `MySQL / PyMySQL` · `OpenAI API` · `Pillow` · `pydub`

## 👤 Author

**Rtamanyu N J**, [@God-Gamer-Manyu](https://github.com/God-Gamer-Manyu)
