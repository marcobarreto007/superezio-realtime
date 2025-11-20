from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, FileReadTool, DirectorySearchTool, DirectoryReadTool

# Initialize tools
# Note: You'll need to set up API keys for some tools or replace them with local alternatives.
# SerperDevTool requires SERPER_API_KEY
search_tool = SerperDevTool()
file_read_tool = FileReadTool()
directory_search_tool = DirectorySearchTool()
directory_read_tool = DirectoryReadTool()

# Define your agents with roles and goals
# For Superezio, we'll imagine a team of programming experts
class SuperezioCrewAgents:
    def __init__(self, llm):
        self.llm = llm # The vLLM engine will be passed here

    def software_architect_agent(self):
        return Agent(
            role='Software Architect',
            goal='Design robust, scalable, and efficient software solutions based on user requirements and existing codebase.',
            backstory="""You are a visionary Software Architect, with decades of experience designing complex systems. 
                         You excel at breaking down problems, identifying optimal technologies, and structuring code for maintainability and performance.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[search_tool, file_read_tool, directory_search_tool]
        )

    def code_developer_agent(self):
        return Agent(
            role='Senior Code Developer',
            goal='Write clean, well-tested, and optimized code following the architect\'s design and best practices.',
            backstory="""You are a meticulous and highly skilled Senior Code Developer. You transform architectural designs into working code,
                         always prioritizing clarity, efficiency, and adherence to project conventions. You are proficient in multiple programming languages.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[file_read_tool, directory_search_tool] # Can read existing code, but generally focuses on writing
        )

    def qa_engineer_agent(self):
        return Agent(
            role='QA Engineer',
            goal='Ensure the quality, reliability, and correctness of the software through comprehensive testing.',
            backstory="""You are a diligent QA Engineer with a keen eye for detail. You write and execute test plans, identify edge cases,
                         and ensure that all code meets the highest quality standards before deployment.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[file_read_tool] # Can read code to understand what to test
        )

# Define tasks for your agents
class SuperezioCrewTasks:
    def __init__(self, superezio_llm):
        self.llm = superezio_llm

    def plan_software_architecture(self, agent, project_description):
        return Task(
            description=f"""Analyze the following project description: '{project_description}'. 
                            Design a high-level software architecture, detailing main components, data flow, and recommended technologies.
                            Output the architecture as a markdown document.""",
            agent=agent,
            expected_output="A markdown document outlining the software architecture."
        )

    def develop_code_from_architecture(self, agent, architecture_doc):
        return Task(
            description=f"""Based on the provided architecture document: '{architecture_doc}', write the necessary code files.
                            Focus on creating the core functionalities as described. Ensure the code is clean, commented, and follows best practices.
                            Output a list of file paths and their content.""",
            agent=agent,
            expected_output="A list of file paths and their corresponding code content (e.g., {'file1.py': 'def func():...', 'file2.js': 'const x = ...'})."
        )

    def review_and_test_code(self, agent, code_files_and_content):
        return Task(
            description=f"""Review the provided code files: '{code_files_and_content}'.
                            Identify potential bugs, suggest improvements, and write unit tests for the main functionalities.
                            Output a review summary and the content of any new test files.""",
            agent=agent,
            expected_output="A review summary and new test file content (e.g., {'review.md': '...', 'test_file1.py': 'import unittest...'})."
        )
