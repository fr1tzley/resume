"""
FIrst of all, want to be able to get all the keywords present in the job. This can be done with spacy probably?

after we have them, we generate a score for which ones are present and which ones aren't

we can guide the AI through a chain of reasoning, using the job description and the interview notes

"""

from pypdf import PdfReader
import spacy
from spacy.matcher import Matcher
import os
import re

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

matcher.add("JOB_EXPERIENCE", [[{"TEXT": {"REGEX":r"\s"}}],
    [{"TEXT": {"REGEX":r"((January|February|March|April|May|June|July|August|September|October|November|December)(\s)([0-9]{4})|Present)"}}]])

import re

def remove_newlines(s):
    # This regex removes \n that are not followed by a capital letter
    return re.sub(r'\n(?![A-Z])', '', s)


def extract_file_text(filepath):
    with open(filepath,"rb") as pdf:
        reader = PdfReader(pdf)

        fulltext = ""

        for p in reader.pages:
            fulltext += p.extract_text()
        return fulltext
    
def extract_resume_info(filepath):
    fulltext = extract_file_text(filepath)
    rest,certifications = fulltext.split(" \nCertifications:  \n")
    rest, education = rest.split("\nEducation:  \n")
    education = education.split("●")
    rest,employment_history = rest.split("\nProfessional  Experience:  \n")
    employment_history = remove_newlines(employment_history)
    employment_history = employment_history.split("\n")
    _,skills = rest.split("\nSkills:  \n")
    #skills = skills.split("●")

    return (employment_history, education, skills, certifications)

def extract_interview_notes(filepath):
    with open(filepath,"rb") as pdf:
        reader = PdfReader(pdf)

        fulltext = ""

        for p in reader.pages:
            fulltext += p.extract_text()
        try:
            rest, job_fit = fulltext.split(" \nJob  Fit:  \n")
            rest, areas_of_improvement = rest.split(" \nAreas  for  Improvement:  \n")
            _, strengths = rest.split(" \nCandidate's  Strengths:  \n")

            return strengths.split("●"), areas_of_improvement.split("●"), re.sub("\n", "", job_fit)
        except Exception as e:
            raise Exception("Error encountered while unpacking interview notes. Maybe check your formatting?")
       
def extract_job_description(filepath):
    with open(filepath,"rb") as pdf:
        reader = PdfReader(pdf)

        fulltext = ""

        for p in reader.pages:
            fulltext += p.extract_text()
        try:
            rest, requirements = fulltext.split(" \nRequirements:  \n")
            rest, responsibilities = rest.split(" \nResponsibilities:  \n")

            return requirements.split("●"), responsibilities.split("●")
        except Exception as e:
            raise Exception("Error encountered while unpacking job description. Maybe check your formatting?")
