# Resume Reader Assignment
 
A simple web-based resume evaluation application.

# Setup
 
Prerequisites:Python 3.12
 
### Setup Steps
- Navigate to the root directory of the git repo.
- Install requirements using pip
``pip install requirements.txt``
- Create a ``.env`` file in the root directory, and add your OpenAI API key. Replace the text ``<your_api_key>`` with your OpenAI API key.
        - For Mac/Linux:``echo "OPENAI_API_KEY=<your_api_key>" > .env``
        - For Windows: ``echo OPENAI_API_KEY=<your_api_key> > .env``
- Start the Flask app by running the file app.py.
        ``python backend/app.y``
- While the app is running, open the ``frontend`` folder, and open ``index.html`` in a browser of your choice.
 
# Explanation
 
 
### Backend
 
The backend is made of 3 major components:The RESTful Flask application, the data scraping component, and the AI analysis component.
 
The Flask service has two simple endpoints, as follows
 
- ``GET \hello``: A simple hello world endpoint to test that the service is actually running.
- ``POST \upload``: A single endpoint that manages uploading the job description, interview notes, and client's resume.
        - It takes the following inputs
                - ``resume``: The applicant's resume.
                - ``job_description``: The description of the job being applied for.
                - ``interview_notes``: Notes from the interview with the client.
        - It returns the following values:
                - ``satisfied_requirements``: The requirements of the job that the AI judged the applicant was suited for.
                - ``unsatisfied requirements``: The requirements of the job the AI judged the applicant was unsuited for.
                - ``interview_fit``: A brief summary of the sentiment expressed by the interview notes.
                - ``strengths``: The strengths of the applicant, as a bullet-point list.
                - ``areas_of_improvement``: The areas the applicant needs to improve, as a bullet point list.
 
 
The data scraping component is quite simple, as PDF data extraction is a very finnicky task that is often quite troublesome. This part of the project uses the PyPDF library to extract text from the PDF, and then uses simple Python string manipulation to extract the necessary information. For a real production application, this would probably be done with a library like spaCy using custom-defined extraction rules. The following data is extracted
 
- From the resume, the program extracts the applicant's work history, educational history, skills, and certifications.
- From the job posting, the program extracts the requirements and responsibilites of the job.
- From the interview notes, the
 
The AI component features several calls to the OpenAI API to convert all the provided documents into a final recommendation. When using LLMs, rather than feeding it all the information at once, it is usually better to guide it through a chain of reasoning-having it draw conclusions on several smaller tasks, and then make it's overall conclusion. Here are the steps of that process.
 
- Using the text of the resume, the AI goes through the job requirements, marking off whether or not that requirement is satisfied and providing a brief explanation. This allows the AI to trim away the irrelevant parts of the resume, while still preserving the necessary components by describing them in the rationale.
- Analyzing the interview, the AI provides a brief summary of the performance, allowing the end user to view the applicant's interview performance without reading the full notes.
- Using the strengths listed in the interview and the list of satisfied requirements it previously created, the AI generates a list of strengths for the applicant.
- Using the areas of improvement listed in the interview and the list of unsatisfied requirements it previously created, the AI generates a list of areas of improvement for the applicant.
- Using all of the previously-generated content, the AI makes a final decision on what it's recommendation for the client is, and expresses it in a brief few-sentence explanation.
 
Each of the pieces of text generated above are returned by the Flask service as a response to the ``upload`` endpoint.
 
### Frontend
The frontend features a simple HTML form that takes the 3 PDF uploads, one for each of the resume, job description, and interview notes. Once the three files are uploaded and submitted, they are sent to the backend's ``\upload`` endpoint for evaluation. While it is waiting for a resposne, the frontend disables the submit button and displays a loading message.
 
Once the backend returns it's results, the frontend redirects to a new page to display them. The overall decision is displayed in a text box, and number boxes directly below display the number of satisfied requirements, unsatisfied requirements, strengths, and areas of improvement found in the applicant's application. Below that, there are text boxes providing written explanation of each of those.
 
# Areas of Improvement
- The project currently uses the untrained default GPT-4o-mini, and it's output parsing is highly brittle and dependent on the formatting that the AI returns it's answer in. This could easily break. This area could be improved by
        - Providing more graceful, principled error handling and more flexible output parsing
        - Using the OpenAI Assistants or Fine-Tuning APIs to ensure the formatting of the output is consistent.
- The parsing of the resume is very simple, highly brittle and extremely dependent on the formatting of the input files. This is fine for a demo, but an actual production application should have much more sophisticated parsing using a natural-language processing library like spaCy, if not another OpenAI model.
- The frontend is quite basic. Adding things like progress bars, colored components to visually indicate a candidate's performance, and so on would make it more visually appealing and easy to parse.
- The frontend only display a simple spinner that doesn't give the user a sense of how long is left to wait, or whether the backend is actually working on fulfilling it's request. It would be useful to add a loading bar and have the backend send periodic updates on the amount of work left to do.
 
