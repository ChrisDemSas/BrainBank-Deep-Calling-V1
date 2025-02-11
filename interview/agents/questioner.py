"""
The Questioner Agent serves to ask questions to the user on their values etc. This agent will have to obtain criticism from the criticizer agent and reword questions accordingly.

Key Features:
    - Be able to ask related questions on the user's prompting.
    - Be able to reword questions based on the evaluator.
"""

import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import logging
from interview.agents.history import ChatHistory
from interview.agents.llm import LLMAgent
from langchain_openai import ChatOpenAI


class Questioner(LLMAgent):
    """The Questioner class serves to ask questions and follow up questions to the user. 

    Attributes:
        api_key: The API key from Anthropic API.
        client: The Claude Agent using LangChain.
        prompt: The prompt to activate the evaluator.
        history: The Chat History of the Evaluator Agent.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize the Questioner class.

        Attributes:
            api_key: The API key from Anthropic API.
        """

        super().__init__(api_key)
        self.question_counter = 0

        self.client = ChatAnthropic(model="claude-3-5-haiku-latest", 
                                    temperature = 0.8,
                                    max_tokens = 1024,
                                    timeout = None,
                                    max_retries = 2,
                                    api_key = api_key)
        
        self.append_history("system", "You are a friend who is interviewing someone to match them with meaningful work. Be as personable as possible.")

        self.critic_prompt = """You are recieving feedback based on how much we know about this user:
        {critique}

        Here is the previous question:
        {response}

        Adjust the question as much as possible, taking into account:
        1) Don't ask investigative work.
        2) Must be a follow up question to the human responses.

        Reword the question, and just output the reworded question.
        """
    
    def generate(self, response: str, critique: str = None) -> str:
        """Take in a response and generate a follow up question.
        
        Attribute:
            response: The response from the user.
            critic: The criticism of the question.
        """

        # Take in a response and a critique
        # Use both in the saved critic response
        # Add a question counter
        # Return the content

        self.append_history("human", self.critic_prompt) # Append evaluator
        prompt = ChatPromptTemplate(self.reveal_chat_history())
        chain = prompt | self.client
        content = chain.invoke({"response": response, "critique": critique}).content
        self.append_history("assistant", content)
        self.question_counter += 1
        return content