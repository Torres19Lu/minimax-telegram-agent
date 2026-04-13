import os
from dataclasses import dataclass
from typing import Dict
import yaml


@dataclass
class Skill:
    name: str
    description: str
    system_prompt: str


def load_skills(skills_dir: str) -> Dict[str, Skill]:
    skills: Dict[str, Skill] = {}
    for filename in sorted(os.listdir(skills_dir)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(skills_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            _, frontmatter, body = content.split("---", 2)
            meta = yaml.safe_load(frontmatter.strip())
            system_prompt = body.strip()
        else:
            meta = {}
            system_prompt = content.strip()

        name = meta.get("name", filename.replace(".md", ""))
        skills[name] = Skill(
            name=name,
            description=meta.get("description", ""),
            system_prompt=system_prompt,
        )
    return skills
