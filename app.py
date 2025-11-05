# -------------------------
# 1️⃣ Imports & API Setup
# -------------------------

import os  # To access environment variables like API keys
from dotenv import load_dotenv  # To load .env file with sensitive data
from openai import OpenAI  # OpenAI client library to call ChatGPT
import panel as pn  # Panel library to build interactive web dashboards

# Load Panel extension (material design optional)
pn.extension(design="material")  # Initializes Panel and sets the design style

# Load API key from .env
load_dotenv()  # Loads environment variables from a .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize OpenAI client with API key


# -------------------------
# 2️⃣ Conversation Memory
# -------------------------

# Initialize conversation memory with a system prompt
# This tells the model its role and instructions (CoT-SC reasoning)
context = [{'role': 'system', 'content': """
You are the Trusted ChatBot, a helpful assistant that generates trusted answers using the CoT-SC (Chain-of-Thought Self-Consistency) method.

For every question:
1. Generate **5 different reasoning paths**.
2. Write each path on a **new line**, in the format:
   Path 1: ...
   Path 2: ...
   Path 3: ...
3. After the 5 paths, write:
   ✅ Final Answer: [your best consistent answer]
Use Markdown formatting with line breaks for readability.
"""}
]

# List to store UI elements for the chat history
panels = []  


# -------------------------
# 3️⃣ Helper Functions
# -------------------------

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    """
    Sends conversation messages to the OpenAI API and returns the assistant's reply.
    - messages: list of dictionaries with 'role' and 'content'
    - model: which OpenAI model to use
    - temperature: controls randomness (0 = deterministic)
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content  # Extract the text reply from API response


def add_message(role, text):
    """
    Adds a message to the conversation memory and updates the Panel UI.
    - role: 'user' or 'assistant'
    - text: message content
    """
    context.append({'role': role, 'content': text})  # Store in conversation memory

    # Assign background colors based on role
    if role == 'assistant':
        color = "#71E883BD"  # light green for bot
    else:
        color = "#94dce6b3"  # light blue for user

    # Create HTML-styled message box with line breaks preserved
    html_text = f"<div style='background-color:{color}; padding:5px; white-space:pre-wrap;'>{text}</div>"

    # Add message row to panels list
    panels.append(pn.Row(f"{role.capitalize()}:", pn.pane.HTML(html_text, width=600)))

    # Update the chat area UI with all messages
    chat_area.objects = list(panels)


# -------------------------
# 4️⃣ Panel Widgets
# -------------------------

# Text input widget for user messages
inp = pn.widgets.TextInput(value="", placeholder="Type your message here…")

# Send button, styled as success (green)
send_btn = pn.widgets.Button(name="Send", button_type="success")

# Reset memory button, styled as danger (red)
reset_btn = pn.widgets.Button(name="Reset Memory", button_type="danger")

# Column to display the chat messages
chat_area = pn.Column()  


# -------------------------
# 5️⃣ Initial Bot Greeting
# -------------------------

def boot_greeting():
    """
    Sends an initial greeting message when the dashboard loads.
    """
    bot_greet = "Hi! I’m TrustedBot. How can I help you today?"
    add_message('assistant', bot_greet)  # Add greeting to chat


# Call the greeting function at startup
boot_greeting()


# -------------------------
# 6️⃣ Callbacks
# -------------------------

def on_send_click(event=None):
    """
    Callback function when Send button is clicked.
    - Sends user message to the model
    - Receives and displays assistant's reply
    """
    user_text = inp.value.strip()  # Get text from input

    # If input is empty, show a friendly warning
    if not user_text:
        add_message('assistant', "Oops! I didn't get that. Could you please type something?")
        return
    
    inp.value = ""  # Clear the input box
    add_message('user', user_text)  # Add user message to chat

    try:
        bot_reply = get_completion_from_messages(context)  # Get bot reply from OpenAI
    except Exception as e:
        bot_reply = "Sorry, something went wrong. Please try again."
        
    add_message('assistant', bot_reply)  # Display bot reply


# Link the callback to the Send button
send_btn.on_click(on_send_click)


def reset_memory(event=None):
    """
    Resets the conversation memory and clears the chat area.
    """
    global context, panels
    context = [context[0]]  # Keep only system prompt
    panels = []  # Clear chat UI
    chat_area.objects = []  # Clear displayed chat
    boot_greeting()  # Show initial greeting again


# Link reset callback to Reset button
reset_btn.on_click(reset_memory)


# -------------------------
# 7️⃣ Layout
# -------------------------

dashboard = pn.Column(
    pn.pane.Markdown("# TrustedBot✅"),  # Main title
    pn.pane.Markdown(
        "### A reasoning-based assistant that generates trusted answers using the CoT-SC (Chain-of-Thought Self-Consistency) method."
    ),  # Description below title
    pn.pane.Markdown(
    "⚠️ **Note:** This chatbot uses **GPT-3.5 Turbo**, which has a knowledge cutoff of September 2021. Data after this date may be unavailable."
    ), # Knowledge cutoff note
    pn.Spacer(height=10),  # Add vertical spacing
    pn.Row(inp, send_btn, reset_btn),  # Input and buttons in one row
    pn.Spacer(height=10),  # Additional spacing
    pn.pane.Markdown("---"),  # Divider line
    chat_area,  # Chat display area
    sizing_mode="stretch_width"  # Stretch elements to full width
)


# -------------------------
# 8️⃣ Show Dashboard
# -------------------------

dashboard.show()  # Launches local web server and opens dashboard in browser