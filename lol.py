import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
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
    
    full_prompt = f"""You are an expert Python data analyst command builder tool. For the user given task: {prompt}, you will construct a command to perform the user given task. As an output only give the python command, nothing else. DATAFRAMES and their DESCRIPTIONS: \n{combined_description}\nAlways pick column names from the dfs to create queries. For any graph/plot, use streamlit chart elements. For example, to plot a line graph, use st.line_chart(df) and for bar graph, use st.bar_chart(df). For any other graph, use the appropriate streamlit chart elements. 
For st.pyplot() pass an object, to keep it thread-safe. As an output only give the python command, nothing else.
    """

    messages = [{"role": "user", "content": full_prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message['content']

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def execute_command(command, dataframes, st):
    try:
        # Create a local variable context containing all DataFrames and additional libraries
        local_vars = {'st': st, 'plt': plt}
        local_vars.update(dataframes)  # Add all DataFrames to the local context

        # Execute the command in the context of the local variables
        exec(f'result = {command}', globals(), local_vars)

        # Check for and handle any plotting commands
        if 'st.line_chart' in command or 'st.bar_chart' in command or 'st.area_chart' in command:
            return "Plot displayed."
        elif 'plt' in command:
            st.pyplot(plt)
            return "Plot displayed."
        else:
            return local_vars.get('result', "Command executed.")
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
st.sidebar.title("DataFrame Information")
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


# for name, df in dataframes.items():
#     df_description = generate_df_description(df, name)
#     st.sidebar.text(df_description)
#     st.sidebar.write("---")

# Initialize session state for conversation and DataFrame
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# Chat interface and interaction
user_prompt = st.text_input("Enter your command:", key="promptUser")
if st.button('Send'):
    st.session_state.conversation.append("User: " + user_prompt)
    command_response = query_gpt4(user_prompt, dataframes)
    # selected_df_name = st.selectbox("Select DataFrame to apply command:", list(dataframes.keys()))
    # selected_df = dataframes[selected_df_name]
    command_result = execute_command(command_response, dataframes, st)
    # dataframes[selected_df_name] = selected_df  # Update the DataFrame
    st.session_state.conversation.append("GPT-4: " + command_response)
    if command_result is not None:
        # Display the DataFrame as a dynamic table in Streamlit
        st.session_state.conversation.append("Result:")
        st.write(command_result)

# Display conversation
for message in st.session_state.conversation:
    if message.startswith("GPT-4:"):
        with st.expander("GPT-4"):
            st.text(message)
    else:
        st.text(message)

# Display DataFrames
for name, df in dataframes.items():
    with st.expander(f"Current DataFrame - {name}"):
        st.write(df)
