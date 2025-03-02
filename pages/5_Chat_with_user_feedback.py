from openai import OpenAI
import streamlit as st
from streamlit_feedback import streamlit_feedback
import trubrics
from datetime import datetime
import pandas as pd
import os
import csv

# CONSTANTS
CSV_PATH = 'database/data.csv'

# Function to log user interactions into the CSV file using pandas
def question_to_csv(question_id, question, answer):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date, time = timestamp.split(" ")

    df = pd.read_csv("database/data.csv")

    # New data to be added
    new_data = {
        'question_id': question_id, 
        'date': date, 
        'time': time, 
        'question': [question], 
        'answer': [answer]
    }

    # Convert the new data into a DataFrame
    new_row = pd.DataFrame([new_data])

    # Concatenate the new row to the existing DataFrame
    df = pd.concat([df, new_row], ignore_index=True)

    # Write the updated DataFrame back to the CSV file with correct formatting
    df.to_csv("database/data.csv", index=False)

    # Print the updated DataFrame
    print("Updated DataFrame:")
    print(df)

def feedback_to_csv(question_id, feedback_type, feedback_text):

    df = pd.read_csv("database/data.csv")
    
    # Update the feedback_type and feedback_text columns
    df.loc[df['question_id'] == question_id, ['feedback_type', 'feedback_text']] = [feedback_type, feedback_text]
    
    df.to_csv("database/data.csv", index=False)

    # Print the updated DataFrame
    print("Updated DataFrame:")
    print(df)
    

# Sidebar for user input
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="feedback_api_key", type="password")

# Title of the app
st.title("📝 Chat with feedback")

# Initialize session state for messages and conversation ID
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you? Leave feedback to help me improve!"}
    ]
if "response" not in st.session_state:
    st.session_state["response"] = None
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = None

# Display chat messages
messages = st.session_state.messages
for msg in messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input for chat
if prompt := st.chat_input(placeholder="Tell me a joke about sharks"):
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Check for OpenAI API key
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    
    # Create OpenAI client and get response
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)

    # Store and display the response
    st.session_state["response"] = response.choices[0].message.content
    st.session_state["conversation_id"] = response.id  # Store conversation ID
    with st.chat_message("assistant"):
        messages.append({"role": "assistant", "content": st.session_state["response"]})
        st.write(st.session_state["response"])

    st.session_state["question_id"] = response.id

    # Log the interaction into the CSV file
    question_to_csv(st.session_state["question_id"], prompt, st.session_state["response"])

# Feedback section
if st.session_state["response"]:
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
        key=f"feedback_{len(messages)}"
    )

    # Feedback we have got the attributes: score, text

    # Print feedback if provided, including conversation ID
    if feedback:
        print("User feedback:", feedback)
        print("Conversation ID:", st.session_state["conversation_id"])  # Log conversation ID with feedback

        feedback_to_csv(st.session_state["question_id"], feedback["score"], feedback["text"])

        