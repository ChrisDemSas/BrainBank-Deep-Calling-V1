"""
The LLM class acts as a parent class to the other agentic classes. 

In this case, this class has a few features which are common to all the other classes:
    - Raising errors when calling APIs
    - Chat history monitoring

"""

import logging
from interview.agents.history import ChatHistory
from typing import List, Tuple


class LLMAgent:
    """
    Initialize the LLMAgent class. The LLM class acts as a parent class to the other agentic classes.
    
    Attributes:
        - api_key: The API Key to access the LLM.
        - chat_history: The Chat History of the LLM Agents.
    """

    api_key: str
    chat_history: ChatHistory

    def __init__(self, api_key: str, curr_history: List[Tuple[str]] = None) -> None:
        """Take in an API Key and initialize the LLM Agent.

        Attributes:
            - api_key: The API Key to access the LLM.
        """

        self.api_key = api_key
        self.chat_history = ChatHistory(history = curr_history)
    
    def check_errors(self, response: str) -> None:
        """Check the errors of the LLM based on the response.
        
        Attributes:
            - response: The response of the LLM.
        """

        raise NotImplementedError

    def append_history(self, role: str, message: str) -> None:
        """Take in a role and message and append it to the chat history.

        Attributes:
            - role: The role of the message.
            - message: The message itself from the user or other LLM Agents.
        """

        self.chat_history.append(role, message)
    
    def reveal_chat_history(self) -> List:
        """Reveals the chat history.
        """

        return self.chat_history.history