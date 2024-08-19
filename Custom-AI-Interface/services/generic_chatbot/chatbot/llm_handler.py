from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate


class LLMHandler:
    def __init__(
        self,
        input_prompt="You are a helpful assistant to answer the given question from the user.",
        temperature=0.2,
        messages=[{"User": "", "Assistant": ""}],
        repetition_penalty=1.1,
        top_k=40,
        top_p=0.95,
        context_length=1024,
    ):
        config = {
            "temperature": temperature,
            "repetition_penalty": repetition_penalty,
            "top_k": top_k,
            "top_p": top_p,
            "context_length": context_length,
        }
        self.model = CTransformers(
            model="TheBloke/neural-chat-7B-v3-1-GGUF",
            model_file="neural-chat-7b-v3-1.Q4_K_M.gguf",
            config=config,
        )

        prompt_history = ""

        for message in messages:
            if message.get("User") != "":
                prompt_history += f"""
                                    ### User: \n{message.get('User')} 
                                    ### Assistant: \n{message.get('Assistant')} 
                                    """
            if len(prompt_history) > (1.5 * context_length):
                prompt_history = ""

        self.template = (
            f"### System: \n {input_prompt} {prompt_history}\n"
            + "\n### User: \n{question}"
            + "\n### Assistant:\n "
        )

    def get_response(self, question):
        prompt = PromptTemplate(template=self.template, input_variables=["question"])

        chain = prompt | self.model
        response = chain.invoke({"question": question})
        return response
