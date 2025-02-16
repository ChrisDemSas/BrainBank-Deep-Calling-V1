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
from typing import List, Tuple


class Questioner(LLMAgent):
    """The Questioner class serves to ask questions and follow up questions to the user. 

    Attributes:
        api_key: The API key from Anthropic API.
        client: The Claude Agent using LangChain.
        prompt: The prompt to activate the evaluator.
        question_counter: The number of questions.
    """

    api_key: str
    client: ChatAnthropic 
    prompt: str
    question_counter: int

    def __init__(self, api_key: str, model: str = "GPT", curr_history: List[Tuple[str]] = None) -> None:
        """Initialize the Questioner class.

        Attributes:
            api_key: The API key from Anthropic API.
            curr_history: The current chat history. Initialized to None.
        """

        super().__init__(api_key, curr_history)
        self.question_counter = 0

        if model == "GPT":
            self.client = ChatOpenAI(model="gpt-4o-mini", 
                                    temperature = 1.0,
                                    max_tokens = 1024,
                                    timeout = None,
                                    max_retries = 2,
                                    api_key = api_key)
        else:
            self.client = ChatAnthropic(model="claude-3-5-haiku-latest", 
                                        temperature = 0,
                                        max_tokens = 1024,
                                        timeout = None,
                                        max_retries = 2,
                                        api_key = api_key)
        
        if curr_history is None:
            self.append_history("system", "You are a friend who is interviewing someone to match them with meaningful work. Be as personable as possible.")

        self.critic_prompt = """
        You have been provided with a critique of the previous question or a user response. If the critique is 'None,' treat the provided response as a user response.

        Critique:
        {critique}

        Previous Question or User Response:
        {response}

        Adjust and reword the next question as follows:

        If the critique is 'None' (i.e., it's a user response):
        Ask an investigative follow-up question that encourages the user to explore new aspects of their response. Avoid narrowing the focus to one specific detail, and ensure the question opens up further lines of conversation.
        
        If a critique is provided:
            Refine and reword the previous question based on the critique.
            Focus on investigative questions that encourage deeper exploration of the user's perspective, avoiding overly specific or speculative questions.
            Maintain a friendly tone to keep the conversation approachable and inviting.
            Ensure the question touches on the user's goals, interests, or values, while encouraging a broader exploration of those themes.
            Output only one question, with some acknowledgement of the response.
        """
    
    def add_question_counter(self) -> None:
        """Increment self.question_counter by 1."""

        self.question_counter += 1
    
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
        return content