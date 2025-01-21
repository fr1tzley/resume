"""
FIrst of all, want to be able to get all the keywords present in the job. This can be done with spacy probably?

after we have them, we generate a score for which ones are present and which ones aren't

we can guide the AI through a chain of reasoning, using the job description and the interview notes

"""

import spacy
from nlp_patterns import SINGLE_BULLET, JOB_PATTERN_2, WORD_COMMA_WORD, DATE_RANGE_ENDING_WITH_PRESENT, DATE_RANGE_ENDING_WITH_YEAR
from read_resume import read_file
from spacy.matcher import Matcher
import os


nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

matcher.add("JOB_EXPERIENCE", [[{"TEXT": {"REGEX":r"\s"}}],
    [{"TEXT": {"REGEX":r"((January|February|March|April|May|June|July|August|September|October|November|December)(\s)([0-9]{4})|Present)"}}]])

def extract_resume(resume_text):
    doc = nlp("June 2015")

    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        print(f"Matched section:\n{span.text}\n")

    return "e"

if __name__ == "__main__":
    print(os.getcwd())
    with open("C:/Users/Owner/Desktop/新しいフォルダー/files/resume.pdf","rb") as file:
        print(extract_resume(read_file(file)))