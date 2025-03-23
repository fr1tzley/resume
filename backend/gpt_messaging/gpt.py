import random
from dotenv import load_dotenv
import os

import openai
from openai import OpenAI, RateLimitError
from openai import AsyncOpenAI
from tiktoken import *

import asyncio

#from gpt_messages import EDUCATION, EXPERIENCES, INTERVIEW_JOB_FIT, INTERVIEW_STRENGTHS, INTERVIEW_WEAKNESSES, REQUIREMENTS, SKILLS
from backend.gpt_messaging.message_utils import custom_question_to_messages, decision_info_to_messages, interview_to_messages, resume_to_messages, strengths_to_messages, weaknesses_to_messages
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
stubbed = False

async def send_messages(messages, max_retries=5, base_delay=10, max_delay=60):
    if stubbed:
        return "3"
    
    counter.add_input_tokens(messages)
    
    attempt = 0
    while True:
        try:
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
            
        except RateLimitError as e:
            attempt += 1
            if attempt > max_retries:
                # We've exceeded our retry limit, so re-raise the exception
                raise
            
            # Calculate the delay with exponential backoff and jitter
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, 0.1 * delay)  # 10% jitter
            total_delay = delay + jitter
            
            print(f"Rate limit exceeded. Retrying in {total_delay:.2f} seconds (attempt {attempt}/{max_retries})...")
            await asyncio.sleep(total_delay)
        
        except Exception as e:
            # For other exceptions, we don't retry
            raise

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
    
async def get_gpt_results(resume_info, interview_info, requirements, responsibilities, custom_questions=[], user_id=-1, job_id=-1):
    experiences, education, skills, certifications = resume_info
    interview_strengths, interview_weakneses, interview_job_fit = interview_info

    resume_messages = resume_to_messages(experiences, education, skills, certifications)
    interview_messages = interview_to_messages(interview_strengths, interview_weakneses, interview_job_fit)

    if custom_questions:
        custom_questions_messages = custom_question_to_messages(resume_messages, interview_messages, requirements, responsibilities, custom_questions)
        custom_questions_task = send_messages(custom_questions_messages)
        custom_question_answers = await custom_questions_task
        custom_question_and_answers = "\n".join([q + "\n" + a for q,a in zip(custom_questions, custom_question_answers)])
        print(custom_question_answers)
        custom_question_and_answers + """1.What is the highest level of education achieved by the applicant?:The applicant has a master's degree.
        2.Does the applicant speak any languages other than English?:They speak Ancient Macedonian."""
    else:
        custom_question_and_answers = ""

    

    requirements_and_rating_task = asyncio.create_task(requirements_fit(resume_messages, requirements))
    requirements_and_rating = await requirements_and_rating_task


    fit_task = asyncio.create_task(interview_notes_fit(interview_messages))
    strengths_task = asyncio.create_task(get_bullet_points(strengths_to_messages(requirements_and_rating, interview_strengths)))
    weaknesses_task = asyncio.create_task(get_bullet_points(weaknesses_to_messages(requirements_and_rating, interview_weakneses)))
    
    fit = await fit_task
    strengths = await strengths_task
    weaknesses = await weaknesses_task
    
    

    decision_msgs = decision_info_to_messages(requirements_and_rating, fit, strengths, weaknesses)
    conclusion_task = asyncio.create_task(send_messages(decision_msgs))
    
    overall_conclusion = (await conclusion_task).split("\n")
    conclusion_oneline, overall_conclusion = overall_conclusion[0], overall_conclusion[-1]

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
        "custom_question_and_answers": custom_question_and_answers,
    }

    retval.update(counter.get_counts())
    counter.reset()
    return retval

def run_get_gpt_results(resume_info, interview_info, requirements, responsibilities, custom_questions=[], user_id=0, job_id=0):
    """Wrapper function to run the async function from synchronous code."""
    return asyncio.run(get_gpt_results(resume_info, interview_info, requirements, responsibilities, custom_questions, user_id, job_id))

if __name__ == "__main__":
    questions = ["What is the highest level of eduation the applicant has achieved?", "Is the applicant proficient with any languages other than English?"]
