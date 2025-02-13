"""
The modules in history.py serves to record the histories of the different chats during the interview. It has 2 classes:
    - ChatHistory: The history of the chat, which includes the users and the LLMs.
    - UserHistory: The history of the user answers.

Key Features:
    - Record Chat History: Each module will effectively record the chat history. 

This module serves to be the short term memory of each conversation. This means that these modules only serves to be the memory for one conversation.
"""

from typing import List, Tuple

class ChatHistory:
    """
    The ChatHistory class. This class aims to save the chat history of each of the items in the conversation, which includes responses by the LLM and user responses. 

    Attributes:
        history: A list of the histories present in the conversation.
    """

    history: List[Tuple[str]]

    def __init__(self, history: List[Tuple[str]] = None) -> None:
        """Initialize the ChatHistory Class."""

        if history is None:
            self.history = []
        else:
            self.history = history
        
    def show_history(self) -> List[Tuple[str]]:
        """Show the history."""

        return self.history
    
    def append(self, role: str, response: str) -> None:
        """Append items to the Chat History Class.
        
        Attributes:
            role: Add the role to the chat history. This must be: assistant, system or human.
            response: The response of the LLM or the user.
        """

        if (role == "assistant") or (role == "system") or (role == "human") or (role == "ai") or (role == "user"):
            self.history.append((role, response))
        else:
            raise ValueError("The role must be: assistant, system, ai, user or human!")

class UserHistory:
    """
    The UserHistory class. This class aims to save the chat history of each of the items in the conversation, which only includes responses by the user responses. 

    Attributes:
        history: A list of the histories present in the conversation by the user.
    """

    history: List[str]
    questions: List[str]

    def __init__(self, past_history: List[List[str]] = None) -> None:
        """Initialize the UserHistory Class."""

        if past_history is None:
            self.history = []
            self.questions = []
        else: # Based on obtain_conversation
            self.history = past_history[1]
            self.questions = past_history[0]
    
    def append_history(self, response: str) -> None:
        """Append items to the self.history.
        
        Attributes:
            response: The response of the user, must be a string.
        """

        if isinstance(response, str):
            self.history.append(response)
        else:
            raise TypeError("Must be a string.")
    
    def append_questions(self, question: str) -> None:
        """Append items to the self.questions.
        
        Attributes:
            question: The question for the user, must be a string.
        """

        if isinstance(question, str):
            self.questions.append(question)
        else:
            raise TypeError("Must be a string.")
    
    def concoctenate_string(self, index: int) -> None:
        """Take in an in index and generate the history of the string by concoctenating.

        Attributes:
            index: How far back the history for concoctenation should be.
        """

        curr = self.history[len(self.history) - index:]
        string = ""

        for s in curr:
            string += s 
        
        return string
    
    def obtain_conversation(self) -> List[List[str]]:
        """Obtain the full conversation."""

        return [self.questions, self.history]