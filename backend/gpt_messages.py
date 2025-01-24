
REQUIREMENTS_TASK_MESSAGE = """You are a helpful assistant helping a company recruit new talent. Your task is to read through the resumes of applicants, compare them to the requirements of the job, and indicate with a Y or N whether the applicant meets that requirement.

The user will send messages explaining the applicants' experiences, skills and education, and will then send the requirements one-by-one. You are to read the resume, and then respond to the requirements as they come.
"""

REQUIREMENTS_INSTRUCTIONS_MESSAGE = """Your instructions are to do the following:
1.Read through the each requirement pasted into the thread.

2.Reference each ofit against the resume sent at the beginning of the chat.

3.Respond with a "Y" if the resume indicates the candidate meets the requirement, and respond with "N" in ALL other cases.

4.On the next line, respond with a short statement explaining your rationale.

5.Repeat the above 2 steps for every requirement that was sent by the user.
"""

INTERVIEW_TASK_MESSAGE = """You are a helpful assistant helping a company recruit new talent. Your task is to read through the results of the interview, and then indicate with a single phrase how well the candidate did on the interview.

The user will send messages with the strengths, areas for improvement and overall impressions recorded by the interviewer. You are to return a single word indicating the interviewer's sentiment, from within the following: [Highly Positive, Positive, Neutral, Negative, Highly Negative], as well as a brief explanation of your decision.
"""

INTERVIEW_INSTRUCTIONS_MESSAGE = """Your instructions are to do the following:
1.Read through each of the sections of the interview notes sent by the user.

2.Consider the sentiment expressed by those messages.

3.Respond with whichever of the following 5 words best expresses their sentiment: [Highly Positive, Positive, Neutral, Negative, Highly Negative].

4.On the next line, explain the reasoning you used to select that option.
"""

STRENGTHS_TASK_MESSAGE = """You are a helpful assistant helping a company recruit new talent. Your task is to read through the results of the interview, the candidate's performance on the individual components of the interview, and the evaluation of their performance on the requirements and responsibilities of the job. Having done that, you are to come up with a list of strengths the candidate has.

The user will send messages with the contents of the interview and the candidate's fit to the individual responsibilities and requirements of the job. Your job is to pick out a list of 1 to 6 strengths of the candidate, and express them as bullet points.
"""

STRENGTHS_INSTRUCTIONS_MESSAGE = """Your instructions are to do the following:
1.Read through each of the sections of the candidate evaluation sent by the user.

2.Consider whether that section indicates a strength of the candidate.

3.Respond with 1 to 6 of the candidate's most significant weaknesses, expressed in bullet points in your own words.
"""

WEAKNESSES_TASK_MESSAGE = """You are a helpful assistant helping a company recruit new talent. Your task is to read through the results of the interview, the candidate's performance on the individual components of the interview, and the evaluation of their performance on the requirements and responsibilities of the job. Having done that, you are to come up with a list of areas of improvement the candidate has.

The user will send messages with the contents of the interview and the candidate's fit to the individual responsibilities and requirements of the job. Your job is to pick out a list of 1 to 4 areas of improvement of the candidate, and express them as bullet points.
"""

WEAKNESSES_INSTRUCTIONS_MESSAGE = """Your instructions are to do the following:
1.Read through each of the sections of the candidate evaluation sent by the user.

2.Consider whether that section indicates a strength of the candidate.

3.Respond with 1 to 4 of the candidate's most significant areas of improvement, expressed in bullet points in your own words.
"""

DECISION_TASK_MESSAGE = """You are a helpful assistant helping a company recruit new talent. Your task is to read through evaluation of the applicant, and provide a decision on whether or not they should be hired by the company.

The user will send the following data:
-A list of the job requirements, along with a message indicating whether the applicant satisfied them, and why or why not.
-A brief explanation of the applicant's performance in the job interview.
-A list of the applicant's strengths with regards to the position.
-A list of the applicant's areas of improvement with regards to the position.

Given all of this information, your task is to provide a recommendation for whether the applicant should be hired or not, explaining your reasoning with reference to the information you have been given.
"""

DECISION_INSTRUCTIONS_MESSAGE = """
1.Read through the information sent by the user.

2.Decide whether the applicant should be hired, and to what degree they are suited for the job.

3.Write a line indicating the result of your decision.

4.On the next line, provide a few sentences summarizing the information the user gave you and how it led you to your decision.
"""



EXPERIENCES = [
    """
    HR Manager, Global Enterprises March 2018 – Present
● Developed and executed HR strategies aligned with business objectives, resulting in a 20% increase in employee retention.
● Managed end-to-end recruitment processes, successfully filling over 100 positions annually.
● Addressed employee grievances and implemented conflict resolution strategies, improving workplace satisfaction by 15%.
● Led performance management initiatives, including annual appraisals and development plans.
● Ensured compliance with labor laws and company policies, reducing legal disputes by 10%.
    """,
    """
HR Generalist, Tech Solutions Inc. June 2015 – February 2018
● Assisted in the recruitment and onboarding of new employees, enhancing the onboarding process efficiency by 25%.
● Managed employee benefits programs, achieving a 95% satisfaction rate among staff.
● Conducted training sessions on company policies and professional development.
● Supported performance management processes, including feedback and coaching.
    """
]

EDUCATION = [
    "M.A. in Human Resources Management University of Tokyo, 2013–2015",
    "B.A. in Business Administration Keio University, 2009–2013"
]

SKILLS = [
    """
    Skills:
    ● HR Management: Talent Acquisition, Employee Relations, Performance Management
    ● HR Systems: Workday, ADP, BambooHR
    ● Legal Compliance: Labor Laws, Employment Regulations
    ● Communication: Negotiation, Conflict Resolution, Presentation
    ● Leadership: Team Building, Staff Development, Strategic Planning
    ● Other: Microsoft Office Suite, Data Analysis
    """
]

INTERVIEW_STRENGTHS = [
    "Extensive experience in HR management, with a focus on talent acquisition and employee relations.",
    "Proficient in HR systems such as Workday and ADP.",
    "Strong understanding of labor laws and HR best practices.",
    "Excellent communication and leadership skills.",
    "Proven track record in developing and implementing HR strategies that align with business objectives."
]

INTERVIEW_WEAKNESSES = [
    "Limited experience with international HR practices; may require additional training for global operations.",
    "Needs to familiarize with the company's specific HR software and tools."
]

INTERVIEW_JOB_FIT = """Taro is a strong candidate for the HR Manager position, bringing a wealth of experience in HR management and a solid understanding of HR systems and legal compliance. His skills align well with the requirements of the role, particularly in talent acquisition and employee relations.
He would be a valuable addition to the team, with a short learning curve to adapt to the company's specific HR tools and international practices.
"""

REQUIREMENTS = [
    "Proven working experience as HR Manager or other HR Executive.",
    "People-oriented and results-driven.",
    "Demonstrable experience with Human Resources metrics.",
    "Knowledge of HR systems and databases.",
    "Ability to architect strategy along with leadership skills.",
    "Excellent active listening, negotiation, and presentation skills.",
    "Competence to build and effectively manage interpersonal relationships at all levels of the company.",
    "In-depth knowledge of labor law and HR best practices.",
    "Degree in Human Resources or related field."
    
]
