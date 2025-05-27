from pydantic import BaseModel, Field, constr
from typing import Optional, List

from typing import List
from pydantic import BaseModel

class ResumeInsight(BaseModel):
    insights: List[str]

class WorkExperience(BaseModel):
 company: str
 role: str
 start_date: Optional[str] = Field(default=None, description="YYYY-MM")
 end_date: Optional[str] = Field(default=None, description="YYYY-MM or Present")
 description: str
class WorkExperienceList(BaseModel):
 work_experiences: List[WorkExperience]



class Education(BaseModel):
 institution: Optional[str]
 degree:Optional[str]
 field: Optional[str]
 start_year: Optional[int]
 end_year: Optional[int]



class EducationList(BaseModel):
    education: List[Education]
class InterviewQuestion(BaseModel):
    question:str
class ResumeMode(BaseModel):
    resume_text: str
    resume_summary: Optional[str] = None
    education_list: Optional[EducationList] = None
    work_experience_list: Optional[WorkExperienceList] = None
    resume_insights:Optional[ResumeInsight] = None
    interview_question_list: List[InterviewQuestion] = Field(default_factory=list)
