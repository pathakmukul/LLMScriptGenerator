Architecture Overview
Frontend: User interface for input parameters and downloading the final PPT.
Backend: Processes input parameters, fetches and analyzes data, generates PPT with GenAI summaries.
Data Layer: Stores raw and processed data, including fetched statistics and generated content.
Hosting: Cloudview for deployment and hosting.
Components
1. Frontend
Technology: HTML, CSS, JavaScript (optional: React.js for a more dynamic UI)
Functionality:
Form for input parameters: Client name, region, peer group
Submit button to trigger backend processing
Download link/button for the generated PPT
2. Backend
Technology: Python (Flask or FastAPI), Python-pptx, GPT API
Modules:
API Endpoint: Receives input parameters from the frontend
Input validation and preprocessing
Data Fetching and Analysis:
Fetch quantitative data from DPI/ANAH cluster
Perform data analysis to extract relevant statistics
Store data in JSON format
Template Identification:
Identify suitable PPT template based on input parameters
Parse the template to identify placeholders
Store placeholder details in JSON format
Content Generation:
Insert data into PPT template from JSON
Use GPT API to generate slide summaries and insert into PPT
PPT Generation:
Finalize and generate the updated PPT
Store or send the PPT file to the frontend
3. Data Layer
Storage: Cloud storage solution or database (e.g., AWS S3, Google Cloud Storage, or a relational database like PostgreSQL)
Data Types:
Raw data fetched from DPI/ANAH cluster
Processed statistics and analysis results
PPT template details and placeholders
Generated content (summaries)
Detailed Workflow
Frontend Interaction:

User inputs client name, region, and peer group on the web form.
User submits the form, triggering an API call to the backend.
Backend Processing:

API Endpoint:
Receives input parameters and validates them.
Passes parameters to the data fetching module.
Data Fetching and Analysis:
Connects to DPI/ANAH cluster and fetches relevant data.
Performs necessary data analysis to extract statistics.
Stores the analyzed data in JSON format.
Template Identification:
Selects an appropriate PPT template based on input parameters.
Parses the template to identify placeholders.
Stores placeholder details in JSON format.
Content Generation:
Inserts statistical data into the selected PPT template using Python-pptx.
Calls GPT API to generate summaries for each slide and inserts them into the template.
PPT Generation:
Finalizes the PPT with all data and summaries inserted.
Stores the final PPT file or sends it back to the frontend.
Frontend Interaction:

Provides a download link or button for the user to download the generated PPT.
Example Directory Structure
graphql
Copy code
sales_pitch_generator/
├── backend/
│   ├── app.py  # Main API entry point
│   ├── data_fetch.py  # Module for data fetching and analysis
│   ├── template_identification.py  # Module for identifying and parsing PPT templates
│   ├── content_generation.py  # Module for generating content and inserting into PPT
│   ├── ppt_generator.py  # Module for finalizing and generating PPT
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html  # Main HTML file
│   ├── styles.css  # CSS styles
│   └── script.js  # JavaScript for frontend logic (if needed)
├── templates/  # Directory for storing PPT templates
└── data/  # Directory for storing raw and processed data
Hosting and Deployment
Cloudview:
Deploy the backend (Flask/FastAPI) as a web service.
Serve the frontend files (HTML/CSS/JavaScript).
Configure storage for the generated PPT files.
CI/CD Pipeline:
Use GitHub Actions, GitLab CI, or another CI/CD tool for automated testing and deployment.
