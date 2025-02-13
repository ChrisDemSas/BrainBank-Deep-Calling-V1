"""
The main Interview Agent serves to conduct interviews with a user by asking follow up questions, critiquing the questions and observing if the responses are enough to obtain a full picture of the person.

Key Features:
    - Ask follow up questions
    - Criticize flow of the interview
    - Create a full picture of the person
    - Save the history of the user.
    - Similarity searches from Pinecone (Not yet implemented)
    - Web Scraping using Beautifulsoup (Not yet implemented)
    - Need to write termination sequence (Not yet implemented)

This is the main component of the interview feature for Brain Bank. After creating a full picture of the person, the assesment is to be matched with impact ventures.
"""

import logging
import asyncio
from interview.agents.questioner import Questioner
from interview.agents.criticizer import Criticizer
from interview.agents.evaluator import Evaluator
from interview.agents.history import ChatHistory, UserHistory
from interview.agents.utils import *
from dotenv import load_dotenv
import os
import time
import uuid
from typing import Tuple, Dict


class InterviewAgent:
    """The Interview Agent class which serves to conduct interviews with a user.

    Attributes:
        name: The name of the interviewee.
        api_key: The API Key for Anthropic API.
        criticizer: The Criticizer Agent.
        evaluator: The Evaluator Agent.
        questioner: The Questioner Agent.
        history: The Tracking of the User History.
        terminator: The Termination Agent.
        id: The id of the interviewee
    """

    def __init__(self, name: str, openai_key: str, anthropic_key: str, question_counter: int, user_history: List[List[str]] = None,
                 criticizer_history: List[List[str]] = None, questioner_history: List[List[str]] = None, evaluator_history: List[List[str]] = None) -> None:
        """Initialize the InterviewAgent.
        
        Attribute:
            name: The name of the interviewee.
            openai_key: OpenAI Key.
            anthropic_key: Anthropic Key.
        """

        if criticizer_history is None:
            self.criticizer = Criticizer(openai_key)
        else:
            self.criticizer = Criticizer(openai_key, curr_history = criticizer_history)
        
        if questioner_history is None:
            self.questioner = Questioner(anthropic_key)
        else:
            self.questioner = Questioner(anthropic_key, curr_history = questioner_history)
        
        if evaluator_history is None:
            self.evaluator = Evaluator(anthropic_key)
        else:
            self.evaluator = Evaluator(anthropic_key, curr_history = evaluator_history)
        
        self.history = UserHistory(past_history=user_history)
        self.terminator = Termination(no_questions = 9)
        self.name = name
        self.id = uuid.uuid4()
        self.question_counter = question_counter

    def obtain_evaluation(self) -> str:
        """Return the current evaluation of the user.
        """

        return self.evaluator.evaluation
    
    def obtain_question_threshold(self) -> int:
        """Return the threshold question."""

        return self.evaluator.threshold

    async def evaluate(self, response: str) -> None:
        """Take in a response and update the evaluation.
        
        Attribute:
            response: The response by the user.
        """

        await self.evaluator.update_evaluation(response)
    
    def _generate_suitable_question(self, response: str = None, critique: str = None) -> str:
        """Take in a response and generate a suitable question depending on the response.

        Attribute:
            response: The response by the user.
        """

        if response is None or response == 'start':

            return self.questioner.generate("Hey! Please ask your first question!")
        elif critique is None:

            return self.questioner.generate(response)
        else:
            
            return self.questioner.generate(response, critique)
    
    def get_response(self, response: str = None) -> str:
        """Generate a response (follow up question) after taking a response.

        Attribute:
            response: The user's response.
        """

        # Check Termination Conditions
        # Generate a followup question
        # Evaluate the person (if applicable): Every 3 questions
            # For every threshold met, create an evaluation.
        # Criticize the question
        # Update the question
        # Return the updated question

        if self.terminator.termination_status():

            return "You're all done! I've compiled a profile on you and I'm ready to direct you to some connections. Type 'Finish' to continue."

        if (response is None) or (response.lower() == 'start'):
            self.question_counter += 1
            return self._generate_suitable_question(None)
        
        question = self._generate_suitable_question(response)
        self.history.append_history(response)

        if (self.question_counter % self.obtain_question_threshold()) == 0 and (self.question_counter > 0):
            print("Updating Evaluation")
            past_history = self.history.concoctenate_string(self.obtain_question_threshold())
            self.evaluator.update_evaluation(past_history)
            question = self._generate_suitable_question(response, critique="Generate a new question that is not similar to any questions asked previously and is related to one of personal values, future goals or personal interests.")
        else:
            evaluation = self.evaluator.generate()
            critique = self.criticizer.generate(question, evaluation)
            question = self._generate_suitable_question(response, critique=critique)
        
        self.history.append_questions(question)
        self.question_counter += 1

        return question
    
    def terminate_interview(self) -> Dict:
        """Terminate the interview."""

        # Update Evaluation
        # Obtain the impression
        # Terminate the interview

        past_history = self.history.concoctenate_string(self.obtain_question_threshold())
        self.evaluator.update_evaluation(past_history)
        impression = self.evaluator.obtain_evaluation()
        curr_time = time.time()
        conversation_history = self.history.obtain_conversation()
        data = self.terminator.terminate(self.id, self.name, curr_time, conversation_history, impression)

        return data

    def prepare_serialization(self) -> Dict:
        """Prepare the data for serialization, so that we can reinitialize the ."""

        # Take out the histories
        evaluator_history = self.evaluator.reveal_chat_history()
        criticizer_history = self.criticizer.reveal_chat_history()
        questioner_history = self.questioner.reveal_chat_history()
        history = self.history.obtain_conversation()

        # Evaluator evaluations
        evaluation = self.evaluator.obtain_evaluation()

        data = {
            "evaluator_history": evaluator_history,
            "criticizer_history": criticizer_history,
            "questioner_history": questioner_history,
            "evaluation": evaluation,
            "history": history,
            "question_counter": self.question_counter
        }

        return data