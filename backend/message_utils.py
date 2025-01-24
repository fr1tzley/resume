from gpt_messages import INTERVIEW_INSTRUCTIONS_MESSAGE, INTERVIEW_TASK_MESSAGE, REQUIREMENTS_INSTRUCTIONS_MESSAGE, REQUIREMENTS_TASK_MESSAGE, STRENGTHS_INSTRUCTIONS_MESSAGE, STRENGTHS_TASK_MESSAGE, WEAKNESSES_INSTRUCTIONS_MESSAGE, WEAKNESSES_TASK_MESSAGE, DECISION_TASK_MESSAGE, DECISION_INSTRUCTIONS_MESSAGE


"""
To get strengths, feed in:
-resume
-matched and unmatched requirements
-interview strengths
-interview job fit

to get areas for improvement, do the same, except use areas for improvement from the interview

"""

def resume_to_messages(experiences,
        education,
        skills):
    messages = [
        {"role": "system", "content": REQUIREMENTS_TASK_MESSAGE},
        {"role": "system", "content": REQUIREMENTS_INSTRUCTIONS_MESSAGE},
        {"role": "user", "content": "These are the candidate's experiences."}
    ]

    for e in experiences:
        messages.append({"role":"user", "content":e})

    messages.append({"role": "user", "content": "This is the candidate's educational history."})

    for e in education:
        messages.append({"role":"user", "content":e})
    
        
    messages.append({"role": "user", "content": "These are the candidate's skills."})
    messages.append({"role":"user", "content": skills[0]})

    return messages 

def interview_to_messages(strengths,
                          weaknesses,
                          job_fit):
    messages = [
        {"role": "system", "content": INTERVIEW_TASK_MESSAGE},
        {"role": "system", "content": INTERVIEW_INSTRUCTIONS_MESSAGE},
        {"role": "user", "content": "These are the candidate's strengths."}
    ]

    for s in strengths:
        messages.append({"role":"user", "content":s})

    messages.append({"role":"user", "content":"These are the candidate's areas of improvement."})

    for w in weaknesses:
        messages.append({"role":"user", "content":w})
    messages += [
        {"role":"user", "content":"This is the interviewer's evaluation of the candidate's job fit."},
        {"role":"user", "content":job_fit}
    ]

    return messages

def strengths_to_messages(requirements,
                          interview_strengths):
    messages = [
        {"role": "system", "content": STRENGTHS_TASK_MESSAGE},
        {"role": "system", "content": STRENGTHS_INSTRUCTIONS_MESSAGE},
        {"role": "user", "content": "These are the candidate's strengths."}
    ]

    for s in interview_strengths:
        messages.append({"role":"user", "content":s})

    messages.append({"role": "user", "content": "This is the candidate's performance on the job requirements."})

    for req, eval, exp in requirements:
        eval = "Yes" if eval == "Y" else "No"
        messages.append({
            "role":"user",
            "content":f"""Requirement:{req} 
            Satisfied?:{eval}
            Explanation:{exp}
            """
        })
    
    return messages
    
def weaknesses_to_messages(requirements,
                          interview_areas_of_improvement):
    messages = [
        {"role": "system", "content": WEAKNESSES_TASK_MESSAGE},
        {"role": "system", "content": WEAKNESSES_INSTRUCTIONS_MESSAGE},
        {"role": "user", "content": "These are the candidate's areas of improvement."}
    ]

    for aop in interview_areas_of_improvement:
        messages.append({"role":"user", "content":aop})

    messages.append({"role": "user", "content": "This is the candidate's performance on the job requirements."})

    for req, eval, exp in requirements:
        eval = "Yes" if eval == "Y" else "No"
        messages.append({
            "role":"user",
            "content":f"""Requirement:{req} 
            Satisfied?:{eval}
            Explanation:{exp}
            """
        })
    
    return messages

def decision_info_to_messages(requirements, interview_performance, strengths, areas_of_improvement, ):
    messages = [
        {"role": "system", "content": DECISION_TASK_MESSAGE},
        {"role": "system", "content": DECISION_INSTRUCTIONS_MESSAGE},   
    ]

    messages.append({"role": "user", "content": "This is the candidate's performance on the job requirements."})
    for req, eval, exp in requirements:
        eval = "Yes" if eval == "Y" else "No"
        messages.append({
            "role":"user",
            "content":f"""Requirement:{req} 
            Satisfied?:{eval}
            Explanation:{exp}
            """
        })
    
    messages.append({"role": "user", "content": "This is a summary of the candidate's interview performance."})
    messages.append({"role": "user", "content": interview_performance})

    messages.append({"role": "user", "content": "These are the candidate's strengths."})
    for s in strengths:
        messages.append({"role":"user", "content":s})

    messages.append({"role": "user", "content": "These are the candidate's areas of improvement."})
    for aop in areas_of_improvement:
        messages.append({"role":"user", "content":aop})

    return messages
