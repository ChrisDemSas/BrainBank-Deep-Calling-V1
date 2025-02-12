"""
The Evaluator Agent serves to evaluate the answers from the user in order to construct a thorough evaluation of a user based on their values, experience, personal interests and future goals.

The Evaluator Agent has the following features:
    - Perform an evaluation of the person.
    - Able to give the final evaluation.
    - Continuously improve upon the evaluation based on the current evaluation.
"""

import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import logging
from interview.agents.history import ChatHistory
from interview.agents.llm import LLMAgent
from langchain_openai import ChatOpenAI


class Evaluator(LLMAgent):
    """The Evaluator Agent works to evaluate the responses by the user so that a good picture of the candidate can be constructed. The agent will work by continuously updating the data.

    Attributes:
        api_key: The API Key to access the LLM.
        client: The Claude Agent using LangChain.
        prompt: The prompt to activate the evaluator.
        history: The Chat History of the Evaluator Agent.
        evaluation: The current evaluation.
        threshold: How many lines of questioning before an evaluation.
    """

    api_key: str
    client: ChatAnthropic
    prompt: str
    history: ChatHistory

    def __init__(self, api_key: str, model: str = "Claude", threshold: int = 3) -> None:
        """Take in an API key and initialize the Evaluator class.

        Attributes:
            api_key: The API Key from Anthropic.
            model: The model either Claude/GPT
            threshold: How many questions before an evaluation
        """

        super().__init__(api_key)

        if model == "GPT":
            self.client = ChatOpenAI(model="gpt-4o-mini", 
                                    temperature = 0,
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
        
        self.evaluation = "A person who is trying to find meaningful work."
        self.threshold = threshold

        self.append_history("system", "You are a life coach who is trying to determine a person's values, future goals, personal interests. Your goal is to have a thorough understanding of the person.")

    def update_evaluation(self, response: str) -> None:
        """Update the evaluation using the answers given."""


        prompt = """Here is a response from a user: {response}. This is your past impression: {evaluation}
            What are your current impressions of this user right now? Combine this new impression with the past impression if there are any, i.e update your current evaluation based on this new information.
            """

        self.append_history("human", response)
        prompt = ChatPromptTemplate(self.reveal_chat_history())
        chain = prompt | self.client

        content = chain.invoke({"response": response, "evaluation": self.evaluation}).content
        self.append_history("assistant", content)
        self.evaluation = content

    def generate(self) -> None:
        """Generate a critique of the current evaluation."""

        # Use the current evaluation (self.evaluation)
        # Use Langchain to invoke a critique
        # Append the history
        # Output the critique as needed

        curr_prompt = """ 
        Here is the current evaluation:
        {evaluation}

        You are to give a one improvement on how the evaluation can be more specific and holistic.
        If there is no substantial critique, output "Continue".
        """

        self.append_history("human", curr_prompt)
        prompt = ChatPromptTemplate(self.reveal_chat_history())
        chain = prompt | self.client
        content = chain.invoke({"evaluation": self.evaluation}).content
        self.append_history("assistant", content)
        return content
    
    def obtain_evaluation(self) -> str:
        """Return self.evaluation."""

        return self.evaluation