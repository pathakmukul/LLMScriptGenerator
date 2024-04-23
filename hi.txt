from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
import openai
from docx import Document
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import PyPDF2
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def AskGPT(prompt, content):
    openai.api_key = OPENAI_API_KEY

    try:
        prompt = prompt
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        GPT_op = response.choices[0].message.content.strip()
        print("GPT OP: ", GPT_op)
        return GPT_op
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return None

   
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('generate_content')
def handle_generate_content(data):
    content = data['content']
    audience = data['audience']
    videoLength = data['video_length']
    category = data['category']
    title = data['title']
    print("11222222222222222222222222222222222222audience: ", title)
    

    category_details = {
    'Case Study': 'Purpose: Generate a comprehensive case study on a specified topic. Structure: Introduction, background, solutions, results, key takeaways. Data: Include data points, graphs, citations. Process: Outline, contextualize, detail issues, explain solutions, present results, summarize takeaways, add citations.',
    'Onboarding': 'Purpose: Create an onboarding guide for a specific role or department. Elements: Company culture, job functions, key contacts, tools, platforms. Process: Structure guide, introduce company, enumerate job functions, list contacts, discuss tools.',
    'Standard Procedures': 'Purpose: Outline standard procedures for a specific task or process. Content: Objectives, prerequisites, step-by-step actions, warnings, precautions. Process: List objectives, prerequisites, detail steps, insert warnings.',
    'Code Walkthrough': 'Purpose: Conduct a code walkthrough for a specific programming task or project. Content: Code snippets, explanations, best practices. Process: Overview of project, include code snippets, explain functionality, discuss best practices.',
    'How-To Videos': 'Purpose: Script a how-to video for a particular task, skill, or process. Structure: Introduction, materials, step-by-step guide, key takeaways. Process: Write introduction, list materials, create narrative, conclude with takeaways.',
    'Cheat Sheets': 'Purpose: Create a cheat sheet for a skill, tool, or process. Content: Tips, shortcuts, essential commands. Process: Compile tips and shortcuts, add commands, organize for quick reference.',
    'Masterclass': 'Purpose: Structure a masterclass on a specific topic or area of expertise. Elements: Learning objectives, in-depth modules, practical exercises, further learning resources. Process: Outline objectives, develop modules, include exercises, list additional resources.',
    'Story': 'Purpose: Write a compelling story. Elements: Engaging plot, character development, setting, climax, resolution. Process: Establish setting, introduce characters, develop plot, build to climax, resolve story.'
}
    category_info = category_details.get(category, "")

    summary_prompt = f"""# MISSION
        You are a Sparse Priming Representation (SPR) writer. You will be given information by the USER here: {content},  which you are to render as an SPR.
        Create a Sparse Primitive Representation of this technical document, which is a code walkthrough. Focus on summarizing the key functions of each code block, explaining the main algorithms, and their practical applications. Aim for a concise yet comprehensive overview that captures the essence of the document's coding content, suitable for readers with basic coding knowledge.
        If not a coding or technical topic, Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human. Use complete sentences.
        In Op only provide the SPR output."""
    
    
    summary = AskGPT(summary_prompt, content)
    emit('content_update', {'type': 'Summary', 'content': summary})
    print("Su1111111111111111111111111mmary: ", summary)

    plan_prompt = f""" # MISSION
You are a Sparse Priming Representation (SPR) decompressor. You will be given an SPR compressed {summary} content which has been written in such a way that makes sense to you.
# METHODOLOGY
Use the input given to you to fully understand and articulate the concept as a plan for the script for a {videoLength} minute long video. Topic: {title}. Audience of the video: {audience}. Category: {category} which should be written with these details {category_info}
provided Instructions:
Section Breakdown: Divide the video into sections, providing a timestamp for each section. Ensure that the total duration aligns with the {videoLength} minute length of the video.
Content Details: For each section, specify the subtopics or key points that should be discussed. This should align with the topic and the associative nature of the topic.
Impute Missing Information: Use inference and reasoning to fill in any gaps in information, ensuring a comprehensive coverage of the topic.
Focus on Plan, Not Script: The output should be a structured plan, not a full script. It should outline what will be discussed in each section, without writing the actual dialogue or narration.
Your plan should serve as a blueprint for creating an informative and engaging video on the complexities and capabilities of content."
"""
    

    video_plan = AskGPT(plan_prompt, content)
    emit('content_update', {'type': 'Plan', 'content': video_plan})
    print("pla11111111111111n_prompt: ", video_plan)

    script_prompt = f"""
You are designed to write scripts for {videoLength} minute corporate training video for the category {category}. Audience of the video: {audience}. Users will provide a detailed plan {video_plan} with timestamps and a source text{content}, which is typically extensive. as a Script Generator, you will thoroughly scan the source text to align content with each section of the video plan.
For each minute of the video, the script should contain around 150 words, within a tolerance range of 140-160 words. This is essential for maintaining the pacing and flow of the video.
SPRScriptGenerator will prioritize technical accuracy and relevance, catering to a corporate employee audience. It will avoid informal language, humor, and personal opinions, maintaining a professional tone throughout. If encountering ambiguous requests, SPRScriptGenerator will independently seek information online to fill knowledge gaps, rather than asking the user for clarifications.
The output will be clear, concise, and strictly relevant to the video plan's topics, ensuring the script is content-rich and effectively communicates the intended message.
Please follow these instructions:
Content Extraction: Carefully read and extract relevant information from the source file for each section of the video plan.
Incorporate Examples: Wherever possible, include examples from the source file to illustrate points more clearly.
Word Count Adherence: Ensure each minute of the script has the required word count. If the initial draft falls short, please revise it to meet the 140-160 words per minute range.
Clarity and Relevance: While focusing on the word count, also ensure the script remains clear, concise, and closely related to the video plan's topics.
This approach will guarantee the script is rich in content, adheres to the specified word count, and effectively communicates the intended message.
    """

    script = AskGPT(script_prompt, content)
    emit('content_update', {'type': 'Script', 'content': script})
    print("s11111111111111111111111111111ript_prompt: ", script)

    # emit('content_update', {
    #     'summary': summary,
    #     'plan': video_plan,
    #     'script': script,
    #     'screenplay': 'Placeholder screenplay content'  # Assuming this needs a similar implementation
    # })

@app.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("files")
    content = ""
    
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(r'L:\VSCodeZone\AEAE\STTT\uploads', filename)
        file.save(file_path)
        
        # Extract text from the file based on its extension
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f.read() + "\n"
        elif filename.endswith('.docx'):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif filename.endswith('.pdf'):
            reader = PyPDF2.PdfFileReader(file_path)
            for page in range(reader.numPages):
                content += reader.getPage(page).extractText() + "\n"
        
        # Remove the file after processing if desired
        # os.remove(file_path)
    
    return jsonify({'content': content})

if __name__ == '__main__':
    socketio.run(app, debug=True)
