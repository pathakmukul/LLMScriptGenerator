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
                content += f.read() + "\n\n"  # Ensure separation between files
        elif filename.endswith('.docx'):
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n\n"  # Ensure separation between files
        elif filename.endswith('.pdf'):
            reader = PyPDF2.PdfFileReader(file_path)
            for page in range(reader.numPages):
                content += reader.getPage(page).extractText() + "\n\n"  # Ensure separation between files

        os.remove(file_path)  # Clean up the file after reading

    return jsonify({'content': content})

if __name__ == '__main__':
    socketio.run(app, debug=True)

    
# ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Training 2323.0</title>
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
                var fileContents = [];

                if (fileInput.files.length > 0) {
                    var filePromises = [];

                    for (let i = 0; i < fileInput.files.length; i++) {
                        formData.append('files', fileInput.files[i]);
                        filePromises.push(readFile(fileInput.files[i]));
                    }

                    console.log("Files appended to FormData:", fileInput.files);

                    Promise.all(filePromises).then(contents => {
                        const combinedContent = contents.join("\n\n");
                        console.log("Combined file contents:", combinedContent);

                        fetch('/upload_files', {
                            method: 'POST',
                            body: formData,
                        })
                        .then(response => response.json())
                        .then(data => {
                            socket.emit('generate_script', { content: combinedContent, ...otherFormData() });
                        })
                        .catch(error => console.error('Error:', error));
                    });
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

            function readFile(file) {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (event) => resolve(event.target.result);
                    reader.onerror = (error) => reject(error);
                    reader.readAsText(file);
                });
            }
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
            padding: 0.5rem 1rem;
            background-color: white;
            border: 1px solid #1434CB;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .downloads-container {
            justify-content: center;
        }
        textarea {
            min-height: 100px;
            max-height: 200px;
            resize: vertical;
        }
        .content-display {
            min-height: 8rem;
            overflow: auto;
            border: 1px solid #1434CB;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .screenplay-content {
            display: none;
            border: 1px solid #1434CB;
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


