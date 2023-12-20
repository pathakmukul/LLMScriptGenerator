import streamlit as st
import pandas as pd
import numpy as np
import openai

# Set up OpenAI API key
openai.api_key = 'sk-'

# Function to generate a description of the DataFrame
def dataframe_description(df):
    description = "DataFrame with columns: "
    description += ", ".join([f"{col} (type: {str(df[col].dtype)})" for col in df.columns])
    return description

# Function to query GPT-4 with DataFrame context
def query_gpt4(prompt, df):
    df_description = dataframe_description(df)
    full_prompt = f""" you are an expert Python data analyst command builder tool. For user given task: {prompt}, you will construct a command to perform the user given task. As an output only give the python command, nothing else. DATAFRAME is named df and here's its DESCRIPTION: {df_description}
    For graph plotting, use st chart elements, select the element as necessary. Ensure the data is in a format compatible with these elements. 

    """
    messages = [{"role": "user", "content": full_prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message['content']

# Function to execute command and handle Streamlit charts
def execute_command(command, df):
    try:
        # Create a local copy of the DataFrame to work with
        local_df = df.copy()
        exec(command, globals(), locals())
        return "Command executed successfully."
    except Exception as e:
        return f"Error executing command: {e}"

# Initialize session state for conversation and DataFrame
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()

# Streamlit UI
st.title('DataFrame Manipulation Chat with GPT-4')

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None:
    st.session_state.dataframe = pd.read_csv(uploaded_file, encoding='latin1')

        # Sidebar information
    st.sidebar.title("DataFrame Information")
    st.sidebar.write("Number of columns:", st.session_state.dataframe.shape[1])
    st.sidebar.write("Number of rows:", st.session_state.dataframe.shape[0])
    st.sidebar.write("Data Types:", st.session_state.dataframe.dtypes)

    numeric_df = st.session_state.dataframe.select_dtypes(include=[np.number])
    st.sidebar.write("Numeric Columns:", numeric_df.columns)

# Chat interface
user_prompt = st.text_input("Enter your command:", key="promptUser")

# Inside the 'Send' button click handler
if st.button('Send'):
    st.session_state.conversation.append("User: " + user_prompt)
    command_response = query_gpt4(user_prompt, st.session_state.dataframe)
    exec_message = execute_command(command_response, st.session_state.dataframe)
    st.session_state.conversation.append("GPT-4: " + command_response)
    st.session_state.conversation.append("System: " + exec_message)

# Display conversation
for message in st.session_state.conversation:
    st.text(message)

st.write("Uploaded DataFrame:")
st.write(st.session_state.dataframe)


# Display current DataFrame
st.write("Happy Analyzing! 💕")
