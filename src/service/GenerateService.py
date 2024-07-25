import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

from src.service.PDFService import PDFService


load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

class GenerateService:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)
    
    def generate(
        self,
        service: str,
        promptText: str,
        pageAnalysis: str,
        pageResult: str,
        pageUseCase: str,
        file_paths: list
    ):  

        outline_prompt = """
            You are an AI language model tasked with generating an outline or table of contents for a new document based on the provided specifications about ****. The document should be structured into three main sections: Analysis, Results, and Case Uses. The total length of the document should be 70 pages, divided as follows:

            Analysis: {xx} pages
            Results: {yy} pages
            Case Uses: {zz} pages
            Follow these steps:

            Analysis ({xx} pages):

            Thoroughly analyze the content of the uploaded files.
            Highlight key insights, data, and trends.
            Discuss the methodology and approach used in the service.
            Provide detailed explanations and interpretations of the data.
            Results ({yy} pages):

            Summarize the findings and outcomes from the analysis.
            Present quantitative and qualitative results.
            Include relevant charts, graphs, and tables for better understanding.
            Discuss the significance of the results and their implications.
            Case Uses ({zz} pages):

            Provide real-world examples and case studies where the service has been applied.
            Detail the benefits and impacts observed in each case.
            Discuss any challenges faced and how they were overcome.
            Include testimonials or quotes from users or stakeholders if available.
            Ensure that the content is well-organized, coherent, and flows logically from one section to the next. Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.

            Outline/Table of Contents:

            Generate a detailed outline or table of contents for the document, including:

            Analysis ({xx} pages):

            Introduction
            Data Collection Methods
            Key Insights and Trends
            Methodology
            Detailed Data Analysis
            Interpretation of Data
            Results ({yy} pages):

            Summary of Findings
            Quantitative Results
            Qualitative Results
            Charts and Graphs
            Significance and Implications
            Case Uses ({zz} pages):

            Case Study 1: [Case Name]
            Case Study 2: [Case Name]
            Case Study 3: [Case Name]
            Benefits and Impacts
            Challenges and Solutions
            Testimonials
            Note: Replace 'xx', 'yy', and 'zz' with the appropriate number of pages based on the total document length of 70 pages and write the number of pages for each section next to the section and heading title. Please write page numbers for each paragraph, section, chapter next to the title. Refer to the uploaded files for all necessary data and information to be included in the document. The final outline/table of contents should clearly indicate the chapters and sections.

            You are also an assistant that generates structured content. I want you to create a book table of contents in JSON format. The structure should include the book title, and a list of chapters. Each chapter should have a chapter number, chapter title, start page, and total pages. Each chapter should also have a list of sections. Each section should have a section number, section title, start page, and total pages.

            Please follow this example format:

            {
            "title": "Sample Book Title",
            "chapters": [
                {
                "chapter_number": 1,
                "chapter_title": "Introduction",
                "start_page": 1,
                "total_pages": 10,
                "sections": [
                    {
                    "section_number": 1.1,
                    "section_title": "Background",
                    "start_page": 1,
                    "total_pages": 5
                    },
                    {
                    "section_number": 1.2,
                    "section_title": "Objective",
                    "start_page": 6,
                    "total_pages": 5
                    }
                ]
                }
                // Add more chapters as needed
                ]
            }
            """
            # Replace placeholders with actual page numbers
        prompt = outline_prompt.replace('xx', str(pageAnalysis)) \
                            .replace('yy', str(pageResult)) \
                            .replace('zz', str(pageUseCase)) \
                            .replace('****', str(service))


        # Create Assistant
        assistant = self.client.beta.assistants.create(
            name="Business Analysis Assistant",
            instructions=prompt,
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )
        
        # Create a vector store caled "Analysis Statements"
        vector_store = self.client.beta.vector_stores.create(name="Analysis Statements")
        
        # Ready the files for upload to OpenAI
        file_streams = [open(path, "rb") for path in file_paths]
        
        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                        vector_store_id=vector_store.id, files=file_streams
                    )
        # You can print the status and the file counts of the batch to see the result of this operation.
        print(file_batch.status)
        print(file_batch.file_counts)
        
        assistant = self.client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        print("create new thread")
        # Create new thread
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": promptText,
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text
        
        # Use regular expression to find text between triple backticks  
        json_string = re.search(r'```json(.*?)```', message_content.value, re.DOTALL).group(1).strip()
        print(json_string)
        outline_object = json.loads(json_string)
        print(outline_object)
        assistant = self.client.beta.assistants.update(
            assistant_id=assistant.id,
            instructions="You are an expert business analyst assistant. Your task is to generate detailed descriptions for sections of a business analysis document.",
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        prompts = []
        for chapter in outline_object['chapters']:
            chapter_info = f"Chapter {chapter['chapter_number']}: {chapter['chapter_title']}\n"
            
            for section in chapter['sections']:
                section_info = f"  Section {section['section_number']}: {section['section_title']}\n"
                section_title = section["section_title"]
                total_pages = section["total_pages"]
                message = self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=section_title
                )
                run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id, assistant_id=assistant.id
                )
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                run_messages = [msg for msg in messages if msg.run_id == run.id]
                if run.status == 'completed':
                    for msg in run_messages:
                        if msg.role == 'assistant':  # Assuming the assistant's role is labeled as 'assistant'
                            print(f"Response for section '{section_title}':")
                            section['descption'] = msg.content[0].text.value
                    section['status'] = run.status
                    print(run.status)
        # print(messages)
        return outline_object
        # return ''
    