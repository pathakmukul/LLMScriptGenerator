from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
from docx import Document
from werkzeug.utils import secure_filename
import PyPDF2
from AskGPT import AskGPT
from promptLib import get_prompts

app = Flask(__name__)
socketio = SocketIO(app)




@app.route('/')
def index():
    return render_template('Aindex.html')
prompts = get_prompts()

@socketio.on('generate_script')
def handle_generate_script(data):
    content = data['content']
    audience = data['audience']
    videoLength = data['video_length']
    category = data['category']
    title = data['title']

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

    summary_prompt = prompts['SPR_Prompt'].format(content=content)
    summary = AskGPT(summary_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Summary', 'content': summary})

    plan_prompt = prompts['Sc_plan_prompt'].format(summary=summary, videoLength=videoLength, title=title, audience=audience, category=category, category_info=category_info)
    video_plan = AskGPT(plan_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Plan', 'content': video_plan})

    script_prompt = prompts['script_prompt'].format(videoLength=videoLength, category=category, audience=audience, video_plan=video_plan, content=content)
    script = AskGPT(script_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Script', 'content': script})


@socketio.on('generate_document')
def handle_generate_document(data):
    title = data['title']
    audience = data['audience']
    category = data['category']
    videoLength = data['video_length']

# call the prompts from the promptLib.py file for Doc_introduction_prompt, Doc_overview_prompt, Doc_content_prompt, and Doc_summary_prompt

    introduction_prompt = prompts['Doc_introduction_prompt'].format(title=title, audience=audience, category=category, videoLength=videoLength)
    introduction = AskGPT(introduction_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Introduction', 'content': introduction})

    overview_prompt = prompts['Doc_overview_prompt'].format(title=title, audience=audience, category=category, videoLength=videoLength)
    overview = AskGPT(overview_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Overview', 'content': overview})

    content_prompt = prompts['Doc_content_prompt'].format(title=title, audience=audience, category=category, videoLength=videoLength)
    document_content = AskGPT(content_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Content', 'content': document_content})

    summary_prompt = prompts['Doc_summary_prompt'].format(title=title, audience=audience, category=category, videoLength=videoLength)
    document_summary = AskGPT(summary_prompt).replace("\n", "<br>")
    emit('content_update', {'type': 'Summary', 'content': document_summary})

    

@app.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("files")
    content = ""
    
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f.read() + "\n"
        elif filename.endswith('.docx'):
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif filename.endswith('.pdf'):
            reader = PyPDF2.PdfFileReader(file_path)
            for page in range(reader.numPages):
                content += reader.getPage(page).extractText() + "\n"
    
    return jsonify({'content': content})

if __name__ == '__main__':
    socketio.run(app, debug=True)



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# PromptLibrary.py

def get_prompts():
    return {
        'SPR_Prompt': """
            You are a Sparse Priming Representation (SPR) writer. You will be given information by the USER here: {content}, which you are to render as an SPR.
            Create a Sparse Primitive Representation of this technical document, which is a code walkthrough. Focus on summarizing the key functions of each code block, explaining the main algorithms, and their practical applications. Aim for a concise yet comprehensive overview that captures the essence of the document's coding content, suitable for readers with basic coding knowledge.
            If not a coding or technical topic, render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human. Use complete sentences.
            In output, only provide the SPR output.
        """,
        'Sc_plan_prompt': """
            You are a Sparse Priming Representation (SPR) decompressor. You will be given an SPR compressed {summary} content which has been written in such a way that makes sense to you.
            Use the input given to you to fully understand and articulate the concept as a plan for the script for a {videoLength} minute long video. Topic: {title}. Audience of the video: {audience}. Category: {category} which should be written with these details {category_info}
            Section Breakdown: Divide the video into sections, providing a timestamp for each section. Ensure that the total duration aligns with the {videoLength} minute length of the video.
            Content Details: For each section, specify the subtopics or key points that should be discussed. This should align with the topic and the associative nature of the topic.
            Impute Missing Information: Use inference and reasoning to fill in any gaps in information, ensuring a comprehensive coverage of the topic.
            Focus on Plan, Not Script: The output should be a structured plan, not a full script. It should outline what will be discussed in each section, without writing the actual dialogue or narration.
            Your plan should serve as a blueprint for creating an informative and engaging video on the complexities and capabilities of content.
        """,
        'script_prompt': """
            You are designed to write scripts for a {videoLength} minute corporate training video for the category {category}. Audience of the video: {audience}. Users will provide a detailed plan {video_plan} with timestamps and a source text {content}, which is typically extensive. As a Script Generator, you will thoroughly scan the source text to align content with each section of the video plan.
            For each minute of the video, the script should contain around 150 words, within a tolerance range of 140-160 words. This is essential for maintaining the pacing and flow of the video.
            SPRScriptGenerator will prioritize technical accuracy and relevance, catering to a corporate employee audience. It will avoid informal language, humor, and personal opinions, maintaining a professional tone throughout. If encountering ambiguous requests, SPRScriptGenerator will independently seek information online to fill knowledge gaps, rather than asking the user for clarifications.
            The output will be clear, concise, and strictly relevant to the video plan's topics, ensuring the script is content-rich and effectively communicates the intended message.
            Please follow these instructions:
            Content Extraction: Carefully read and extract relevant information from the source file for each section of the video plan.
            Incorporate Examples: Wherever possible, include examples from the source file to illustrate points more clearly.
            Word Count Adherence: Ensure each minute of the script has the required word count. If the initial draft falls short, please revise it to meet the 140-160 words per minute range.
            Clarity and Relevance: While focusing on the word count, also ensure the script remains clear, concise, and closely related to the video plan's topics.
            This approach will guarantee the script is rich in content, adheres to the specified word count, and effectively communicates the intended message.
        """,     
        'Doc_introduction_prompt': """
                Generate an introduction for a document titled '{title}', targeted at {audience}. The category is '{category}' and the document should align with a video length of {videoLength} minutes. Provide an engaging and informative introduction that sets the stage for the rest of the content.
            """,
        'Doc_overview_prompt':"""
                Provide an overview for a document titled '{title}', targeted at {audience} in the '{category}' category. The document should complement a video with a length of {videoLength} minutes. The overview should summarize the main points and provide a clear outline of what the document will cover.
            """,
        'Doc_content_prompt': """
                Generate the main content for a document titled '{title}', intended for {audience} in the '{category}' category. The document supports a video of {videoLength} minutes. Detail the core topics and ensure comprehensive coverage of the subject matter.
            """,
        'Doc_summary_prompt': """
                Create a summary for a document titled '{title}', aimed at {audience} within the '{category}' category. The summary should encapsulate the key points of the document, aligning with a video duration of {videoLength} minutes.
            """

    }


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import openai
from dotenv import load_dotenv
import os
from flask import Flask

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SECRET_KEY'] = 'your_secret_key_here'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')




def AskGPT(prompt):
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

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Training 23.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.2/FileSaver.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('download-button').addEventListener('click', function() {
                var summary = "Summary:\n" + document.getElementById('summary-content').textContent + "\n";
                var plan = "Plan:\n" + document.getElementById('plan-content').textContent + "\n";
                var script = "Script:\n" + document.getElementById('script-content').textContent + "\n";
                var screenplay = "Screenplay:\n" + document.getElementById('screenplay-content').textContent + "\n";
                var content = summary + plan + script + screenplay;
                var blob = new Blob([content], {type: "text/plain;charset=utf-8"});
                saveAs(blob, "script.doc");
            });

            const button = document.getElementById('generate-button');
            const docButton = document.getElementById('generate-Document');
            const title = document.querySelector('[name="title"]');
            const audience = document.querySelector('[name="audience"]');
            const category = document.querySelector('[name="category"]');
            const videoLength = document.querySelector('[name="video-length"]');
            const content = document.querySelector('[name="content"]');
            const fileInput = document.querySelector('[name="files"]');
            var generateButton = document.getElementById('generate-button');
            var tabButtonLabels = {
                'script': ['Summary', 'Plan', 'Script', 'Screenplay'],
                'document': ['Introduction', 'Overview', 'Content', 'Summary']
            };

            function updateButtonState() {
                const allFieldsFilled = title.value && audience.value && category.value && videoLength.value && (content.value || fileInput.files.length);
                button.disabled = !allFieldsFilled;
                docButton.disabled = !allFieldsFilled;
            }

            [title, audience, category, videoLength, content, fileInput].forEach(field => {
                field.addEventListener('change', updateButtonState);
            });

            updateButtonState(); // Call on page load to set initial button state

            function updateTabLabels(type) {
                let tabs = document.querySelectorAll('.tab-button');
                let labels = tabButtonLabels[type];
                tabs.forEach((tab, index) => {
                    tab.textContent = labels[index];
                    tab.setAttribute('data-content', labels[index].toLowerCase() + '-content');
                });
                // Reset the content display
                document.querySelectorAll('.content-area > div').forEach(content => content.style.display = 'none');
                document.querySelector('.tabs-container').style.display = 'flex'; // Ensure tabs are visible
                tabs[0].click(); // Click the first tab to show its content
            }

            
        function otherFormData() {
            return {
                title: title.value,
                audience: audience.value,
                category: category.value,
                video_length: videoLength.value
            };
        }

        var socket = io();

        button.addEventListener('click', function() {
            var formData = new FormData();
            if (fileInput.files.length > 0) {
                for (let i = 0; i < fileInput.files.length; i++) {
                    formData.append('files', fileInput.files[i]);
                }
                console.log("Files appended to FormData:", fileInput.files);
                fetch('/upload_files', {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Server response:", data);
                    socket.emit('generate_script', { content: data.content, ...otherFormData() });
                })
                .catch(error => console.error('Error:', error));
            } else {
                console.log("No files uploaded, using text content");
                socket.emit('generate_script', { content: content.value, ...otherFormData() });
            }
            updateTabLabels('script');
        });

        docButton.addEventListener('click', function() {
            socket.emit('generate_document', otherFormData());
            updateTabLabels('document');
        });

        socket.on('content_update', function(data) {
            console.log("Content update received:", data);
            switch (data.type) {
                case 'Summary':
                    document.getElementById('summary-content').innerHTML = data.content;
                    document.getElementById('summary-content').style.display = 'block';
                    break;
                case 'Plan':
                    document.getElementById('plan-content').innerHTML = data.content;
                    document.getElementById('plan-content').style.display = 'block';
                    break;
                case 'Script':
                    document.getElementById('script-content').innerHTML = data.content;
                    document.getElementById('script-content').style.display = 'block';
                    break;
                case 'Screenplay':
                    document.getElementById('screenplay-content').innerHTML = data.content;
                    document.getElementById('screenplay-content').style.display = 'block';
                    break;
                case 'Introduction':
                    document.getElementById('introduction-content').innerHTML = data.content;
                    document.getElementById('introduction-content').style.display = 'block';
                    break;
                case 'Overview':
                    document.getElementById('overview-content').innerHTML = data.content;
                    document.getElementById('overview-content').style.display = 'block';
                    break;
                case 'Content':
                    document.getElementById('content-content').innerHTML = data.content;
                    document.getElementById('content-content').style.display = 'block';
                    break;
            }
            document.querySelector('.tabs-container').style.display = 'flex';
            document.querySelector('.downloads-container').style.display = 'flex';
        });

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', function() {
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                    const contentId = btn.getAttribute('data-content');
                    document.getElementById(contentId).style.display = 'none';
                });
                button.classList.add('active');
                const contentToShowId = button.getAttribute('data-content');
                document.getElementById(contentToShowId).style.display = 'block';
            });
        });

        document.querySelector('.tab-button').click();
    });

 
    </script>
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
        }
        .btn-visa-blue {
            background-color: #1434CB; /* Visa blue */
            color: white;
        }
        .border-visa-blue {
            border-color: #1434CB; /* Visa blue */
        }
        .content-display {
            min-height: 8rem;
            overflow: auto;
            border: 1px solid #1434CB;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: white;
            border-radius: .5rem;
        }
        .tabs-and-content-container {
            display: flex;
            flex-direction: row;
        }
        .tabs-container {
            display: flex;
            flex-direction: column;
            margin-right: 1rem;
        }
        .tab-button {
            background-color: #F7F7F7;
            color: #1434CB;
            border: 2px solid #1434CB;
            padding: 0.5rem 1rem;
            margin-bottom: 0.25rem;
            cursor: pointer;
            text-align: left;
            border-radius: 0.5rem;
            width: 100%;
        }
        .tab-button.active {
            background-color: #FCC015;
            color: white;
        }
        .content-area {
            flex-grow: 1;
            border: 2px solid #1434CB;
            padding: 1rem;
            border-radius: 0.5rem;
        }
    </style>
</head>
<body class="flex flex-col h-full bg-gray-50 text-gray-800">
    <div class="flex-grow">
        <header class="bg-[#1434CB] text-white sticky top-0 z-50">
            <div class="container mx-auto flex justify-between items-center p-4">
                <h1 class="text-2xl font-bold" style="color: white;">SMAR<span style="color: #FCC015; font-size: 1.5em;">T</span>RAINING</h1>
                <div>
                    <img src="https://cdn.visa.com/v2/assets/images/logos/visa/blue/logo.png" alt="Visa Logo" class="h-8">
                </div>
            </div>
        </header>
        <div class="container mx-auto p-6">
            <div class="mb-4">
                <input type="text" name="title" placeholder="Working TITLE" class="w-full p-2 border border-visa-blue rounded mb-3">
                <div class="flex space-x-2 mb-3">
                    <select name="audience" class="p-2 border border-visa-blue rounded">
                        <option selected disabled>Select Audience</option>
                        <option>Developer</option>
                        <option>Product Manager</option>
                        <option>Executives</option>
                        <option>Sales</option>
                    </select>
                    <select name="category" class="p-2 border border-visa-blue rounded">
                        <option selected disabled>Select Category</option>
                        <option>Training</option>
                        <option>Case Study</option>
                        <option>Onboarding</option>
                        <option>Standard Procedures</option>
                        <option>Code Walkthrough</option>
                        <option>How-To Videos</option>
                        <option>Cheat Sheets</option>
                        <option>Masterclass</option>
                        <option>Story</option>
                    </select>
                    <input name="video-length" type="number" placeholder="Video Length" class="w-full p-2 border border-visa-blue rounded" min="2" max="8">
                </div>
                <input type="file" name="files" multiple class="mb-3">
                <textarea name="content" placeholder="Enter your content here" class="w-full p-2 border border-visa-blue rounded mb-3"></textarea>
                <div class="flex justify-center mt-3">
                    <button id="generate-button" class="p-2 btn-visa-blue rounded mr-2">Generate!</button>
                    <button id="generate-Document" class="p-2 btn-visa-blue rounded">Generate Doc!</button>
                </div>
            </div>
            <div class="tabs-and-content-container">
                <div class="tabs-container" style="display: none;">
                    <button class="tab-button" data-content="summary-content">Summary</button>
                    <button class="tab-button" data-content="plan-content">Plan</button>
                    <button class="tab-button" data-content="script-content">Script</button>
                    <button class="tab-button" data-content="screenplay-content">Screenplay</button>
                </div>
                <div class="content-area">
                    <div id="summary-content" style="display: none;">Summary appears here</div>
                    <div id="plan-content" style="display: none;">Plan Summary appears here</div>
                    <div id="script-content" style="display: none;">Script Summary appears here</div>
                    <div id="screenplay-content" style="display: none;">Screenplay Summary appears here</div>
                    <div id="introduction-content" style="display: none;">Introduction appears here</div>
                    <div id="overview-content" style="display: none;">Overview appears here</div>
                    <div id="content-content" style="display: none;">Content appears here</div>
                </div>
            </div>
            <br>
            <br>
            <div class="flex space-x-2 downloads-container" style="display: none;">
                <button class="p-2 btn-visa-blue rounded">Download Screenplay</button>
                <button id="download-button" class="p-2 btn-visa-blue rounded">Download Script</button>
            </div> 
        </div>
    </div>
    <footer class="bg-gray-100 mt-auto">
        <div class="container mx-auto p-6 text-gray-800">
            <div class="text-center text-sm mt-4">
                © 2024 Smart Training 2.0. All rights reserved.
            </div>
        </div>
    </footer>
</body>
</html>
