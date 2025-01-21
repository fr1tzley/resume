class Resume:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

        self.skills = []
        self.experience = []
        self.education = []
        self.certifications = []


    def add_skill(self, skill_name, skill_type):
        self.skills.append(
            {
            "skill": skill_name,
            "type": skill_type
            }
        )
    
    def add_experience(self, title, description, start, end):
        self.experiences.append(
            {
                "job_title": title,
                "job_description": description,
                "start": start,
                "end": end
            }
        )

    def add_education(self, title, insitution, start, end):
        self.education.append({
            "title": title,
            "institution": insitution,
            "start": start,
            "end": end
        })

    def add_certification(self,certification):
        self.certifications.append(certification)