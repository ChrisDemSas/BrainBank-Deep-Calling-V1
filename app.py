### TO DO: Flask app

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, g
from interview.main import InterviewAgent
from interview.agents.utils import Termination
from match.matcher import Matcher
import json
import os
import pickle

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


NAME = "John Doe"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


@app.route('/')
def home() -> None:
    """Render the initial template."""

    session['name'] = NAME
    session['openai'] = OPENAI_API_KEY
    session['anthropic'] = ANTHROPIC_API_KEY
    session['evaluator_history'] = None
    session['questioner_history'] = None
    session['criticizer_history'] = None
    session['evaluation'] = "A person who is trying to find meaningful work."
    session['history'] = None
    session['question_counter'] = 0

    return render_template('index.html')

@app.route('/get_response', methods = ["POST"])
def get_response() -> json:
    """Get a response and generate a question."""

    message = request.form["message"]
    interview_agent = InterviewAgent(
        session['name'], 
        session['openai'],
        session['anthropic'],
        question_counter=session['question_counter'],
        user_history=session['history'],
        criticizer_history=session['criticizer_history'],
        questioner_history=session['questioner_history'],
        evaluator_history=session['evaluator_history']
    )

    interview_agent.evaluator.replace_evaluation(session['evaluation']) # Replace Evaluation
    interview_agent.question_counter = session['question_counter'] # Question Counter replacing

    response = interview_agent.get_response(message)

    # Update Session Data
    data = interview_agent.prepare_serialization()
    session['name'] = NAME
    session['openai'] = OPENAI_API_KEY
    session['anthropic'] = ANTHROPIC_API_KEY
    session['evaluator_history'] = data['evaluator_history']
    session['questioner_history'] = data['questioner_history']
    session['criticizer_history'] = data['criticizer_history']
    session['evaluation'] = interview_agent.evaluator.obtain_evaluation()
    session['history'] = data['history']
    session['question_counter'] = data['question_counter']

    return jsonify({"question": response})

@app.route('/get_match', methods = ["GET"])
def get_match() -> json:
    """Get a match based on the line of questioning."""

    interview_agent = InterviewAgent(
        session['name'], 
        session['openai'],
        session['anthropic'],
        question_counter=session['question_counter'],
        user_history=session['history'],
        criticizer_history=session['criticizer_history'],
        questioner_history=session['questioner_history'],
        evaluator_history=session['evaluator_history']
    )

    user_attributes = interview_agent.terminate_interview()
    matcher = Matcher(user_attributes, "match/data.csv") # Relative Path for the Data For Now
    matches = matcher.match() # Returns a dictionary of matches

    return jsonify(matches)

if __name__ == "__main__":
    app.run()