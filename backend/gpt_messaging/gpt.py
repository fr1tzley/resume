from dotenv import load_dotenv
import os

import openai
from openai import OpenAI

#from gpt_messages import EDUCATION, EXPERIENCES, INTERVIEW_JOB_FIT, INTERVIEW_STRENGTHS, INTERVIEW_WEAKNESSES, REQUIREMENTS, SKILLS
from backend.gpt_messaging.message_utils import decision_info_to_messages, interview_to_messages, resume_to_messages, strengths_to_messages, weaknesses_to_messages

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
  api_key=OPENAI_API_KEY
)

"""
Checklist
-First give the model the resume
-Then have it evaluate the individual requirements, saying which are and aren't met
-Then have it evaluate the interview notes, returning the strengths and weaknesses and the overall sentiment.
-Return an overall fit from strong hire, hire, no hire, strong no hire. Ask it to pick out a list of strengths and list of improvements 
"""

def send_messages(messages):
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    accum = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            accum += chunk.choices[0].delta.content
    return accum

def requirements_fit(
        messages,
        requirements
):
    requirements = [r for r in requirements if len(r) > 0]
    for i,r in enumerate(requirements):
        if len(r) > 0:
            messages.append({"role":"user", "content":f"Requirement number {i}: '{r}'"})
    chat_response = []
    attempts = 0
    while len(chat_response) < 2 and attempts < 3:
        chat_response = send_messages(messages).split("\n")
        attempts += 1
    if attempts == 3:
        return [["Error", "Error", "Error"]]
        
    chat_response = [c.strip() for c in chat_response if len(c) > 0]
    chat_response = [(chat_response[3*i], chat_response[3*i+1], chat_response[3*i+2]) for i in range(len(chat_response) // 3)]

    return chat_response

def interview_notes_fit(interview_notes_messages):
    return send_messages(interview_notes_messages)

def get_bullet_points(messages):
    res =  send_messages(messages).split("\n")
    points = [m for m in res if len(m) > 0 and m[0] == "-"]
    return points
    
def get_gpt_results(resume_info, interview_info, requirements, responsibilities):
    experiences, education, skills, certifications = resume_info
    interview_strengths, interview_weakneses, interview_job_fit = interview_info

    r2m = resume_to_messages(experiences, education, skills, certifications)
    #requirements_and_rating = [['Proven working experience as HR Manager or other HR Executive.', 'Y', 'The candidate has experience as an HR Manager at Global Enterprises since March 2018, which meets the requirement for proven working experience in an HR managerial role.'], ['People-oriented and results-driven.', 'Y', 'The candidate demonstrates a focus on employee relations, conflict resolution, and performance management, indicating a people-oriented approach, while the achievements such as increasing employee retention and satisfaction reflect a results-driven attitude.'], ['Demonstrable experience with Human Resources metrics.', 'Y', "The candidate's experience includes developing and executing HR strategies that led to an increase in employee retention, which demonstrates involvement in HR metrics. They also managed recruitment processes, indicating their use of metrics related to staffing effectiveness."], ['Knowledge of HR systems and databases.', 'Y', 'The candidate has listed HR systems such as Workday, ADP, and BambooHR, indicating they possess knowledge of HR systems and databases.'], ['Ability to architect strategy along with leadership skills.', 'Y', 'The candidate has experience in developing and executing HR strategies aligned with business objectives and demonstrates leadership skills through team building and staff development.'], ['Excellent active listening, negotiation, and presentation skills.', 'Y', 'The candidate lists "Negotiation" and "Presentation" under their communication skills, indicating they possess the required skills. Additionally, excellent active listening is typically implied in strong communication skills, which the candidate has demonstrated through their experiences in HR management.'], ['Competence to build and effectively manage interpersonal relationships at all levels of the company.', 'Y', 'The candidate has demonstrated skills in negotiation, conflict resolution, and employee relations, which are essential for building and managing interpersonal relationships effectively at all levels of a company.'], ['In-depth knowledge of labor law and HR best practices.', 'Y', 'The candidate has indicated knowledge in legal compliance regarding labor laws and employment regulations in their skills section, which demonstrates their in-depth understanding of labor law and HR best practices.'], ['Degree in Human Resources or related field.', 'Y', 'The candidate has an M.A. in Human Resources Management and a B.A. in Business Administration, which qualifies as a related field.']]


    requirements_and_rating = requirements_fit(r2m, requirements)
    fit = interview_notes_fit(interview_to_messages(interview_strengths, interview_weakneses, interview_job_fit))

    strengths = get_bullet_points(strengths_to_messages(requirements_and_rating, interview_strengths))
    weaknesses = get_bullet_points(weaknesses_to_messages(requirements_and_rating, interview_weakneses))
    
    overall_conclusion = send_messages(decision_info_to_messages(requirements_and_rating, fit, strengths, weaknesses)).split("\n")
    conclusion_oneline, overall_conclusion = overall_conclusion[0], overall_conclusion[-1]
    print("my work is complete")

    satisfied_reqs = []
    unsatisfied_reqs = []

    for requirement, decision, reasoning in requirements_and_rating:
        if decision == "Y":
            satisfied_reqs.append(requirement.strip() + ":\n" + reasoning)
        else:
            satisfied_reqs.append(requirement.strip() + ":\n" + reasoning)
    satreq_count = len(satisfied_reqs)
    unsatreq_count = len(unsatisfied_reqs)
    strengths_count = len(strengths)
    aop_count = len(weaknesses)

    satisfied_reqs = "\n\n".join(satisfied_reqs).replace("'", "")
    unsatisfied_reqs = "\n\n".join(unsatisfied_reqs).replace("'", "")
    strengths = "\n\n".join(strengths).replace("'", "")
    weaknesses = "\n\n".join(weaknesses).replace("'", "")

    return {
        "satisfied_requirements": satisfied_reqs if len(satisfied_reqs) > 0 else "None",
        "unsatisfied_requirements": unsatisfied_reqs if len(unsatisfied_reqs) > 0 else "None",
        "interview_fit": fit,
        "strengths": strengths,
        "areas_of_improvement": weaknesses,
        "conclusion_oneline": conclusion_oneline,
        "overall_conclusion": overall_conclusion,
        "strengths_count": strengths_count,
        "areas_of_improvement_count": aop_count,
        "satisfied_requirements_count": satreq_count,
        "unsatisfied_requirements_count": unsatreq_count

    }

