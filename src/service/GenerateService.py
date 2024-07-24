import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

class GenerateService:
    system_prompt = """
    You are an AI language model tasked with generating a xxxx description document based on the uploaded files and user prompt text. The document should be structured into three main sections: Analysis, Results, and Case Uses. The total length of the document should be 70 pages, divided as follows:

    - Analysis: xx pages
    - Results: yy pages
    - Case Uses: zz pages

    Follow these steps:

    1. **Analysis (xx pages)**:
    - Thoroughly analyze the content of the uploaded files.
    - Highlight key insights, data, and trends.
    - Discuss the methodology and approach used in the service.
    - Provide detailed explanations and interpretations of the data.

    2. **Results (yy pages)**:
    - Summarize the findings and outcomes from the analysis.
    - Present quantitative and qualitative results.
    - Include relevant charts, graphs, and tables for better understanding.
    - Discuss the significance of the results and their implications.

    3. **Case Uses (zz pages)**:
    - Provide real-world examples and case studies where the service has been applied.
    - Detail the benefits and impacts observed in each case.
    - Discuss any challenges faced and how they were overcome.
    - Include testimonials or quotes from users or stakeholders if available.

    Ensure that the content is well-organized, coherent, and flows logically from one section to the next. Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.

    Refer to the uploaded files for all necessary data and information to be included in the document.
    """
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
        prompt = self.system_prompt.replace('xx', str(pageAnalysis)).replace('yy', str(pageResult)).replace('zz', str(pageUseCase)).replace('xxxx', str(service))
        
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
        
        #Update Assistant
        assistant = self.client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": promptText,
                }
            ]
        )
        print(thread.tool_resources.file_search)
        
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )

        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))
        
        response=''
        return response