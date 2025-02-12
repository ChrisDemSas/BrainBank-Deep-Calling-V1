"""
The criticizer agent works to actively criticize the questioner agent with regard to the types of questions being generated. 

The criticizer agent will have the following features:
    - Directing missing personality information from the evaluator.
    - Turning these personality information into criticism.
"""
import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging
from interview.agents.history import ChatHistory
from interview.agents.llm import LLMAgent


class Criticizer(LLMAgent):
    """The Criticizer agent. This class aims to provide meaningful critique to shape the question in the direction of the conversation.

    Attributes:
        api_key: The API Key to access the LLM.
        user_history: The past evaluation of the criticizer if there is any (Most likely queried from the database).
        client: The Claude Agent using LangChain.
        prompt: The prompt to activate the criticizer.
        history: The Chat History of the Criticizer Agent.
    """

    api_key: str
    user_past: str
    client: ChatAnthropic
    prompt: str
    history: ChatHistory

    def __init__(self, api_key: str, user_past: str = None, model: str = "GPT") -> None:
        """
        Take in an API Key and user history and initialize the Criticizer Agent.

        Attributes:
            api_key: The API Key for Anthropic AI.
            user_history: Past personality assesment of the user.
            model: The model of the agent.
        """

        super().__init__(api_key)

        if model == "GPT":
            self.client = ChatOpenAI(model="gpt-4o-mini", 
                                    temperature = 1.0,
                                    max_tokens = 1024,
                                    timeout = None,
                                    max_retries = 2,
                                    api_key = api_key)
        elif model == "Claude":
            self.client = ChatAnthropic(model="claude-3-5-haiku-latest", 
                                        temperature = 1.0,
                                        max_tokens = 1024,
                                        timeout = None,
                                        max_retries = 2,
                                        api_key = api_key)
        
        self.user_past = user_past
        self.prompt = """The following is the question from a conversation:
        {question}

        Here is the current personality evaluation based on previous conversations with this user:
        {evaluation}

        If the evaluation is simply: "Continue." Then I want you to suggest a critique which indicates that you want a completely different question which pertains to personal values, personal goals or personal interests.

        Otherwise, I want you to provide a meaningful critique to the question based on the personality evaluation. More specifically, what can the questioner do to make the evaluation more specific and confident? 
        Limit your critique to 1 paragraph (50 words) but do not suggest any questions directly.
        """

        self.append_history("system", "You are a manager who is giving constructive criticism on how to make your worker's work better.")
    
    def generate(self, question: str, evaluation: str) -> str:
        """Take in a question and evaluation from an LLM and generate a critique of the question.

        Attributes:
            question: The question from the questioner agent.
            evaluation: The personality evaluation from the evaluator agent.
        """

        # Append the question to the chat history
        # Feed the question to the model via prompting
        # Evaluate the question and obtain a critique
        # Append the assistant to the chat history
        # Return the critique

        self.append_history("human", self.prompt)
        prompt = ChatPromptTemplate(self.reveal_chat_history())
        chain = prompt | self.client
        content = chain.invoke({"question": question, "evaluation": evaluation}).content
        self.append_history("assistant", content)
        return content