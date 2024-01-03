import streamlit as st
import numpy as np
import pandas as pd
import openai
import matplotlib.pyplot as plt
import os
# Function to read CSV files and handle encoding issues
def read_csv_file(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        return pd.read_csv(uploaded_file, encoding='latin1')


# Set up OpenAI API key
openai.api_key = 'sk-'

# Function to generate a description of each DataFrame
def generate_df_description(df, df_name):
    description = f"{df_name}: {df.shape[0]} rows, {df.shape[1]} columns\n"
    for col in df.columns:
        description += f"- {col} (type: {str(df[col].dtype)})\n"
    return description

def generate_df_descriptions(dataframes):
    descriptions = {}
    for df_name, df in dataframes.items():
        description = f"{df_name}: {df.shape[0]} rows, {df.shape[1]} columns\n"
        for col in df.columns:
            description += f"- {col} (type: {str(df[col].dtype)})\n"
        descriptions[df_name] = description
    return descriptions

# Function to query GPT-4 with multiple DataFrame contexts
def query_gpt4(prompt, dataframes):
    df_descriptions = generate_df_descriptions(dataframes)
    combined_description = "\n".join(df_descriptions.values())
    
    full_prompt = f"""You are an expert Python data analyst. For the user given task: {prompt}, you will construct a python query to perform the user given task. As an output only give the python command, nothing else. DATAFRAMES and their DESCRIPTIONS: \n{combined_description}\nAlways pick column names from the dfs to create queries. For any visualisation, use streamlit(st) chart elements, use the appropriate streamlit chart elements. 
    As your response will be directly executed in Python without changes, make sure to only give the python code; no other text, no comments and not even imports. Display visualisations in streamlit not matplotlib elements

    """

    messages = [{"role": "user", "content": full_prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    print(response.choices[0].message['content'])
    return response.choices[0].message['content']

def GPTANALYZER(dataframes, user_prompt, gpt_reply, results):
    df_descriptions = generate_df_descriptions(dataframes)
    combined_description = "\n".join(df_descriptions.values())

    analysis_prompt = f"""Data Analysis Request:
DataFrames Description:{combined_description} User Prompt: {user_prompt} GPT-4 Reply: {gpt_reply} Results: {results}Based on the above information, please provide your analysis and observations as a data analyst.
If the {results} contains "No output generated by the command" or "Error executing command", please only reply: "Try again"
when {results} contain review, Provide a summary of the reviews to act as overall review of the store. Also, justify revenue generated by the store with respect to the review."""
    messages = [{"role": "user", "content": analysis_prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message['content']


def ReDoQuery(dataframes, user_prompt, gpt_reply, results):
    df_descriptions = generate_df_descriptions(dataframes)
    combined_description = "\n".join(df_descriptions.values())

    redoPrompt = f""" You are given
    User's ask: {user_prompt}
    All dataframe information: {combined_description}
    Python query built by AI: {gpt_reply} and
    Result of the Py query: {results}
    Based on the error message found in Result, Please rewrite a better user's ask for GPT AI to understand better and be able to perform the user's ask without the error. Your reply should be an extension to user's ask with error handling condition. The consumer of your putput would be another GPT app just like you.
    Never use the word "Error" in your reply.
"""
    messages = [{"role": "user", "content": redoPrompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message['content']



import matplotlib.pyplot as plt

import io
import contextlib

# def execute_command(command, dataframes, st):
#     try:
#         local_vars = {'st': st, 'plt': plt}
#         local_vars.update(dataframes)

#         # Directly execute the command
#         exec(command, globals(), local_vars)

#         # Check if the command is for plotting
#         if 'st.bar_chart' in command or 'st.pyplot' in command:
#             return "Plot displayed."
#         elif 'result' in local_vars:
#             return local_vars['result']
#         else:
#             return "No output generated by the command."
#     except Exception as e:
#         return f"Error executing command: {e}"
def execute_command(command, dataframes, st):
    try:
        local_vars = {'st': st, 'plt': plt, 'np': np}
        local_vars.update(dataframes)

        exec(command, globals(), local_vars)

        if 'plt' in command:
            # Save the plot to a file
            plot_filename = 'plot.png'
            plt.savefig(plot_filename)
            plt.close()
            # Store the filename in session state
            st.session_state['plot_filename'] = plot_filename
            return "Plot displayed and saved."
        elif 'result' in local_vars:
            return local_vars['result']
        else:
            return "No output generated by the command."
    except Exception as e:
        return f"Error executing command: {e}"







            
# Initialize session state for conversation and DataFrame
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()

# Streamlit UI
st.title('Multi-CSV DataFrame Viewer with GPT-4 Assistance')

# File uploader
uploaded_files = st.file_uploader("Upload CSV Files", type=["csv"], accept_multiple_files=True)

dataframes = {}
if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        df_name = f"df{i+1}"  # Naming DataFrames as df1, df2, ...
        dataframes[df_name] = read_csv_file(uploaded_file)

# Display DataFrame information in the sidebar
st.sidebar.title("lol5 DataFrame Information")
selected_df_name = st.sidebar.selectbox("Select a DataFrame:", list(dataframes.keys()))
if selected_df_name:
    selected_df = dataframes[selected_df_name]  # Retrieve the selected DataFrame
    df_description = generate_df_description(selected_df, selected_df_name)
    
    st.sidebar.text(df_description)
    st.sidebar.write(f"DataFrame: {selected_df_name}")
    st.sidebar.write("Number of columns:", selected_df.shape[1])
    st.sidebar.write("Number of rows:", selected_df.shape[0])
    st.sidebar.write("Data Types:", selected_df.dtypes)
    st.sidebar.write("---")

# Chat interface and interaction

# Initialize session state for conversation and DataFrame
if 'messages' not in st.session_state:
    st.session_state.messages = []

chat_placeholder = st.empty()

with chat_placeholder.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_prompt = st.chat_input("Enter your command:")
if user_prompt:
    # Update chat with user input immediately
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with chat_placeholder.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    query_response = query_gpt4(user_prompt, dataframes)
    command_result = execute_command(query_response, dataframes, st)



    if not isinstance(command_result, str):
        command_result = str(command_result)
    # Check for error in command result
    if "Error executing command" in command_result:
        modified_prompt = ReDoQuery(dataframes, user_prompt, query_response, command_result)
        st.session_state.messages.append({"role": "user", "content": "Modified Prompt: " + modified_prompt})  # Add modified prompt to chat
        query_response = query_gpt4(modified_prompt, dataframes)
        command_result = execute_command(query_response, dataframes, st)

    analysis_response = GPTANALYZER(dataframes, user_prompt, query_response, str(command_result))
    st.session_state.messages.extend([
        {"role": "query", "content": query_response},
        {"role": "result", "content": command_result},
        {"role": "assistant", "content": analysis_response}
    ])
    with chat_placeholder.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["content"] == "Plot displayed and saved.":
                    if 'plot_filename' in st.session_state:
                        plot_filename = st.session_state['plot_filename']
                        # Display the saved plot image
                        st.chat_message("Grapher").image(plot_filename)
                        # Optionally, delete the image file after displaying it
                        os.remove(plot_filename)
                        del st.session_state['plot_filename']
                else:
                    st.write(message["content"])

    # with chat_placeholder.container():
    #     for message in st.session_state.messages:
    #         with st.chat_message(message["role"]):
    #             st.write(message["content"])
    st.rerun()
    # Display conversation
# Use markdown to create a horizontal line for separation
st.markdown("---")

# Display DataFrames
for name, df in dataframes.items():
    with st.sidebar.container():
        with st.expander(f"Current DataFrame = {name}"):
            st.dataframe(df)
