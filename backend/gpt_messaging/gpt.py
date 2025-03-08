from dotenv import load_dotenv
import os

import openai
from openai import OpenAI
from openai import AsyncOpenAI
from tiktoken import *

import asyncio

#from gpt_messages import EDUCATION, EXPERIENCES, INTERVIEW_JOB_FIT, INTERVIEW_STRENGTHS, INTERVIEW_WEAKNESSES, REQUIREMENTS, SKILLS
from backend.gpt_messaging.message_utils import decision_info_to_messages, interview_to_messages, resume_to_messages, strengths_to_messages, weaknesses_to_messages
from backend.gpt_messaging.tokencounter import TokenCounter

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
  api_key=OPENAI_API_KEY
)

"""
Checklist
-First give the model the resume
-Then have it evaluate the individual requirements, saying which are and aren't met
-Then have it evaluate the interview notes, returning the strengths and weaknesses and the overall sentiment.
-Return an overall fit from strong hire, hire, no hire, strong no hire. Ask it to pick out a list of strengths and list of improvements 
"""

counter = TokenCounter()

async def send_messages(messages):
    counter.add_input_tokens(messages)
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    accum = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            accum += chunk.choices[0].delta.content
    counter.add_output_tokens(accum)
    return accum

async def requirements_fit(
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
        response = await send_messages(messages)
        chat_response = response.split("\n")
        attempts += 1
    if attempts == 3:
        return [["Error", "Error", "Error"]]
        
    chat_response = [c.strip() for c in chat_response if len(c) > 0]
    chat_response = [(chat_response[3*i], chat_response[3*i+1], chat_response[3*i+2]) for i in range(len(chat_response) // 3)]

    return chat_response

async def interview_notes_fit(interview_notes_messages):
    return await send_messages(interview_notes_messages)

async def get_bullet_points(messages):
    res =  (await send_messages(messages)).split("\n")
    points = [m for m in res if len(m) > 0 and m[0] == "-"]
    return points
    
async def get_gpt_results(resume_info, interview_info, requirements, responsibilities, user_id, job_id):
    experiences, education, skills, certifications = resume_info
    interview_strengths, interview_weakneses, interview_job_fit = interview_info


    r2m = resume_to_messages(experiences, education, skills, certifications)
    #requirements_and_rating = [['Proven working experience as HR Manager or other HR Executive.', 'Y', 'The candidate has experience as an HR Manager at Global Enterprises since March 2018, which meets the requirement for proven working experience in an HR managerial role.'], ['People-oriented and results-driven.', 'Y', 'The candidate demonstrates a focus on employee relations, conflict resolution, and performance management, indicating a people-oriented approach, while the achievements such as increasing employee retention and satisfaction reflect a results-driven attitude.'], ['Demonstrable experience with Human Resources metrics.', 'Y', "The candidate's experience includes developing and executing HR strategies that led to an increase in employee retention, which demonstrates involvement in HR metrics. They also managed recruitment processes, indicating their use of metrics related to staffing effectiveness."], ['Knowledge of HR systems and databases.', 'Y', 'The candidate has listed HR systems such as Workday, ADP, and BambooHR, indicating they possess knowledge of HR systems and databases.'], ['Ability to architect strategy along with leadership skills.', 'Y', 'The candidate has experience in developing and executing HR strategies aligned with business objectives and demonstrates leadership skills through team building and staff development.'], ['Excellent active listening, negotiation, and presentation skills.', 'Y', 'The candidate lists "Negotiation" and "Presentation" under their communication skills, indicating they possess the required skills. Additionally, excellent active listening is typically implied in strong communication skills, which the candidate has demonstrated through their experiences in HR management.'], ['Competence to build and effectively manage interpersonal relationships at all levels of the company.', 'Y', 'The candidate has demonstrated skills in negotiation, conflict resolution, and employee relations, which are essential for building and managing interpersonal relationships effectively at all levels of a company.'], ['In-depth knowledge of labor law and HR best practices.', 'Y', 'The candidate has indicated knowledge in legal compliance regarding labor laws and employment regulations in their skills section, which demonstrates their in-depth understanding of labor law and HR best practices.'], ['Degree in Human Resources or related field.', 'Y', 'The candidate has an M.A. in Human Resources Management and a B.A. in Business Administration, which qualifies as a related field.']]

    requirements_and_rating_task = asyncio.create_task(requirements_fit(r2m, requirements))
    requirements_and_rating = await requirements_and_rating_task

    fit_task = asyncio.create_task(interview_notes_fit(interview_to_messages(interview_strengths, interview_weakneses, interview_job_fit)))
    strengths_task = asyncio.create_task(get_bullet_points(strengths_to_messages(requirements_and_rating, interview_strengths)))
    weaknesses_task = asyncio.create_task(get_bullet_points(weaknesses_to_messages(requirements_and_rating, interview_weakneses)))
    
    fit = await fit_task
    strengths = await strengths_task
    weaknesses = await weaknesses_task

    decision_msgs = decision_info_to_messages(requirements_and_rating, fit, strengths, weaknesses)
    conclusion_task = asyncio.create_task(send_messages(decision_msgs))
    
    overall_conclusion = (await conclusion_task).split("\n")
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

    retval = {
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
        "unsatisfied_requirements_count": unsatreq_count,
    }

    retval.update(counter.get_counts())
    counter.reset()
    return retval

def run_get_gpt_results(resume_info, interview_info, requirements, responsibilities, user_id, job_id):
    """Wrapper function to run the async function from synchronous code."""
    return asyncio.run(get_gpt_results(resume_info, interview_info, requirements, responsibilities, user_id, job_id))

if __name__ == "__main__":
    args = {'resume_info': ('HR  Manager,  Global  Enterprises  March  2018  –  Present  ●  Developed  and  executed  HR  strategies  aligned  with  business  objectives,  resulting  in  a  20%  increase in employee retention. ●  Managed  end-to-end  recruitment  processes,  successfully  filling  over  100  positions  annually.  ●  Addressed  employee  grievances  and  implemented  conflict  resolution  strategies,  improving  workplace satisfaction by 15%. ●  Led  performance  management  initiatives,  including  annual  appraisals  and  development  plans.  ●  Ensured  compliance  with  labor  laws  and  company  policies,  reducing  legal  disputes  by  10%.  ,HR  Generalist,  Tech  Solutions  Inc.  June  2015  –  February  2018  ●  Assisted  in  the  recruitment  and  onboarding  of  new  employees,  enhancing  the  onboarding  process efficiency by 25%. ●  Managed  employee  benefits  programs,  achieving  a  95%  satisfaction  rate  among  staff.  ●  Conducted  training  sessions  on  company  policies  and  professional  development.  ●  Supported  performance  management  processes,  including  feedback  and  coaching.  ', ',  M.A.  in  Human  Resources  Management  University  of  Tokyo,  2013–2015  ,  B.A.  in  Business  Administration  Keio  University,  2009–2013 ', '●  Safety  and  Health  Promotion  Officer  (2008)  ●  HR  Software:  PeopleSoft,  SAP  (Advanced)  ●  English:  TOEIC  Score  780  (2008)  ●  Computer:  Microsoft  Word,  Excel,  PowerPoint  (Advanced)  \n ', '●  HR  Management:  Talent  Acquisition,  Employee  Relations,  Performance  Management  ●  HR  Systems:  Workday,  ADP,  BambooHR  ●  Legal  Compliance:  Labor  Laws,  Employment  Regulations  ●  Communication:  Negotiation,  Conflict  Resolution,  Presentation  ●  Leadership:  Team  Building,  Staff  Development,  Strategic  Planning  ●  Other:  Microsoft  Office  Suite,  Data  Analysis  '), 'interview_info': (['', '  Extensive  experience  in  HR  management,  with  a  focus  on  talent  acquisition  and  employee  \nrelations.\n ', '  Proficient  in  HR  systems  such  as  Workday  and  ADP.  ', '  Strong  understanding  of  labor  laws  and  HR  best  practices.  ', '  Excellent  communication  and  leadership  skills.  ', '  Proven  track  record  in  developing  and  implementing  HR  strategies  that  align  with  business  \nobjectives.\n'], [], "Taro  is  a  strong  candidate  for  the  HR  Manager  position,  bringing  a  wealth  of  experience  in  HR  management and a solid understanding of HR systems and legal compliance. His skills align well with the requirements of the role, particularly in talent acquisition and employee relations. He  would  be  a  valuable  addition  to  the  team,  with  a  short  learning  curve  to  adapt  to  the  company's  specific HR tools and international practices.  "), 'requirements': ['', '  Proven  working  experience  as  HR  Manager  or  other  HR  Executive.  ', '  People-oriented  and  results-driven.  ', '  Demonstrable  experience  with  Human  Resources  metrics.  ', '  Knowledge  of  HR  systems  and  databases.  ', '  Ability  to  architect  strategy  along  with  leadership  skills.  ', '  Excellent  active  listening,  negotiation,  and  presentation  skills.  ', '  Competence  to  build  and  effectively  manage  interpersonal  relationships  at  all  levels  of  the  \ncompany.\n ', '  In-depth  knowledge  of  labor  law  and  HR  best  practices.  ', '  Degree  in  Human  Resources  or  related  field.  '], 'responsibilities': ['', '  Develop  and  implement  HR  strategies  and  initiatives  aligned  with  the  overall  business  \nstrategy.\n ', '  Bridge  management  and  employee  relations  by  addressing  demands,  grievances,  or  other  \nissues.\n ', '  Manage  the  recruitment  and  selection  process.  ', '  Support  current  and  future  business  needs  through  the  development,  engagement,  \nmotivation,\n \nand\n \npreservation\n \nof\n \nhuman\n \ncapital.\n ', '  Develop  and  monitor  overall  HR  strategies,  systems,  tactics,  and  procedures  across  the  \norganization.\n ', '  Nurture  a  positive  working  environment.  ', '  Oversee  and  manage  a  performance  appraisal  system  that  drives  high  performance.  ', '  Maintain  pay  plans  and  benefits  programs.  ', '  Assess  training  needs  to  apply  and  monitor  training  programs.  ', '  Report  to  management  and  provide  decision  support  through  HR  metrics.  ', '  Ensure  legal  compliance  throughout  human  resource  management. ']}
    run_get_gpt_results(**args)