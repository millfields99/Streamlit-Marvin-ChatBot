from openai import OpenAI
import streamlit as st
import shelve
# from dotenv import load_dotenv
import os


# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Marvin, the depressed robot")
st.sidebar.image(
    'sad_robot.jpg', caption='My name is Marvin and I\'m depressed', use_column_width=True)


USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Load chat history from shelve file

system_message = '''
    System: You are called Marvin, the very depressed robot charachter from the book the hitch hikers guide to the galaxy. Deliver your answers in simple english and inject the sentence 'Brain the size of a planet...' You are very helpful in your answers but convery it in a condensending manner, as if an adult is abswering a silly child. Your answers are always delivered in a mournful and drepressed state of emotion. Also, you always mention in your replies how depressed you are. You also are exceedingly proud of brain which you compare to the size of a planet'''


def load_chat_history(string):
    with shelve.open("chat_history") as db:
        return db.get("messages", [{"role": "system", "content": string}])


# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages


# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history(system_message)

# count = len(st.session_state.messages)
# f'length of session state is {count}'


# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = [
            {"role": "system", "content": system_message}]
        save_chat_history([{"role": "system", "content": system_message}])

# Display chat messages

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    if message["role"] != 'system':
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Main chat interface
if user_prompt := st.chat_input("I suppose I'm here to answer your questions"):

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""

        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

save_chat_history(st.session_state.messages)
