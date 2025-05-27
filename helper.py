import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
# from IPython.display import Image, display
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.checkpoint.memory import MemorySaver

from model import *

load_dotenv()

class ResumeGraph:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,
            max_retries=5,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        self.output_parser_work = PydanticOutputParser(pydantic_object=WorkExperienceList)
        self.output_parser_education = PydanticOutputParser(pydantic_object=EducationList)
        self.output_parser_resume_insights = PydanticOutputParser(pydantic_object=ResumeInsight)
        self.output_parser_question = PydanticOutputParser(pydantic_object=InterviewQuestion)
        self.graph = self._build_graph()

    def parse_resume(self, state: ResumeMode):
        response = self.llm.invoke(f"""
        Act as a resume parser and extract entire resume in below format only:
        resume_text:{state.resume_text}
        {self.output_parser_work.get_format_instructions()} 
        """)
        res = self.output_parser_work.parse(response.content)
        state.work_experience_list = res
        return state

    def parse_education(self, state: ResumeMode):
        response = self.llm.invoke(f"""
        Act as a resume parser and extract Education details of resume in below format only:
        resume_text:{state.resume_text}
        {self.output_parser_education.get_format_instructions()} 
        """)
        res = self.output_parser_education.parse(response.content)
        state.education_list = res
        return state

    def generate_summary(self, state: ResumeMode):
        response = self.llm.invoke(f"""
        Act as an HR assistant and summarize in detail way the below resume:

        Work Experience:
        {state.work_experience_list}

        Education:
        {state.education_list}
        """)
        return state

    def extract_insights(self, state: ResumeMode):
        response = self.llm.invoke(f"""
        Act as HR assistant and extract list insights from below resume details:
        Work Experience:
        {state.work_experience_list}

        Education:
        {state.education_list}
                            
        {self.output_parser_resume_insights.get_format_instructions()}
        """)
        res = self.output_parser_resume_insights.parse(response.content)
        state.resume_insights = res
        return state

    def generate_question(self, state: ResumeMode):
        response = self.llm.invoke(f"""
        Act as HR assistant and generate one question based on below resume insights of the candidate. Don't repeat same questions:
        resume insight:{state.resume_insights}
        previous_question_list:{state.interview_question_list}   
        {self.output_parser_question.get_format_instructions()}           
        """)
        res = self.output_parser_question.parse(response.content)
       
        state.interview_question_list.append(res)
        return state

    def _build_graph(self):
        builder = StateGraph(ResumeMode)
        
        # Add nodes
        builder.add_node("work_experience_parser", self.parse_resume)
        builder.add_node("education_parser", self.parse_education)
        builder.add_node("summarizer", self.generate_summary)
        builder.add_node("resume_insight", self.extract_insights)
        builder.add_node("generate_question", self.generate_question)

        # Add edges
        builder.add_edge(START, "work_experience_parser")
        builder.add_edge("work_experience_parser", "education_parser")
        builder.add_edge("education_parser", "summarizer")
        builder.add_edge("summarizer", "resume_insight")
        builder.add_edge("resume_insight", "generate_question")

        memory = MemorySaver()
        return builder.compile(checkpointer=memory)

    def process_resume(self, resume_text: str) -> ResumeMode:
        """
        Process a resume text through the graph and return the final state.
        
        Args:
            resume_text (str): The resume text to process
            
        Returns:
            ResumeMode: The final state containing all processed information
        """
        initial_state = ResumeMode(resume_text=resume_text)
        return self.graph.invoke(initial_state)