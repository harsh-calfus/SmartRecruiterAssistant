import re

def process_prompt(prompt):
    skills = []
    years = 0

    skills_list = ["Python", "Java", "SQL", "Django", "AWS"]

    for skill in skills_list:
        if skill.lower() in prompt.lower():
            skills.append(skill)

    exp_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?)', prompt)
    if exp_match:
        years = int(exp_match.group(1))

    return skills, years