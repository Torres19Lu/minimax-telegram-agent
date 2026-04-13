import os
from skills.loader import load_skills, Skill


def test_load_skills():
    skills = load_skills(os.path.join(os.path.dirname(__file__), "../../skills"))
    assert "default" in skills
    assert "coder" in skills
    assert "writer" in skills
    assert skills["default"].name == "default"
    assert "助手" in skills["default"].system_prompt
