"""Here, we have the utility functions or classes, namely the termination sequence of the interview program.

This file will have the following classes:
    - Termination: The termination steps an interview sequence undertakes.
"""

import logging
import time
from typing import List, Tuple


class Termination:
    """
    The Termination class which terminates the interview sequence. 

    Attributes:
        no_questions: The number of questions before termination.
    """

    def __init__(self, no_questions: int = 0) -> None:
        """Initialize the Termination class.
        
        Attributes:
            no_questions: The number of questions before termination.
        """

        self.no_questions = no_questions
        self.condition = False
    
    def termination_status(self) -> bool:
        """Check the termination status."""

        return self.condition

    def check_terminate_questions(self, curr_questions: int) -> str:
        """Terminate the interview based on the number of questions.
        
        Attributes:
            curr_questions: Number of current questions.
        """

        if curr_questions >= self.no_questions:
            self.terminate = True
    
    def terminate(self, id: str, name: str, time: time, conversation_history: List[List[str]], impression: str) -> str:
        """Terminate the interview based on the attribute (eg, specific string, number of questions etc.).
        
        Attributes:
            id: The ID of the interview.
            name: Name of interviewee.
            time: The current time.
            conversation_history: The question and answer history. The 0'th index is the questions, and the 1st index is the answers ([questions_list, answer_list]).
            impression: The current impression
        """

        # Process the conversation history into a dictionary
        question_answer = {}
        question_history, answer_history = conversation_history
        
        for index, questions in enumerate(question_history):
            answer = answer_history[index]
            question_answer[questions] = answer

        # Turn the data into an API
        data = {"id": id,
                "name": name,
                "time": time,
                "question_answer": question_answer,
                "impression": impression}
        
        return data