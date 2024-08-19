from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate


class LLMHandler:
    def __init__(self):
        config = {"temperature": 0.1, "context_length": 8192}
        self.model = CTransformers(
            model="TheBloke/neural-chat-7B-v3-1-GGUF",
            model_file="neural-chat-7b-v3-1.Q4_K_M.gguf",
            config=config,
        )
        self.template = (
            "### System: \n You are a helpful assistant to convert text to "
            + "PyMongo query.Answer exactly in one line from the schema. "

            + "\n### User: \n{question}"
            + "\n### Assistant:\n "
        )

    def get_response(self, question):
        prompt = PromptTemplate(template=self.template, input_variables=["question"])
        chain = prompt | self.model
        response = chain.invoke({"question": question})
        return response
