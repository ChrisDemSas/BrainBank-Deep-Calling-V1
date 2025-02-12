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


@app.before_request
def before_request():
    g.interview_agent = InterviewAgent("John Doe", os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"))


@app.route('/')
def home() -> None:
    """Render the initial template."""

    return render_template('index.html')

@app.route('/get_response', methods = ["POST"])
def get_response() -> json:
    """Get a response and generate a question."""

    message = request.form["message"]
    interview_agent = g.interview_agent
    response = interview_agent.get_response(message)
    return jsonify({"question": response})

@app.route('/get_match', methods = ["GET"])
def get_match() -> json:
    """Get a match based on the line of questioning."""

    interview_agent = g.interview_agent
    user_attributes = interview_agent.terminate_interview()
    matcher = Matcher(user_attributes, "match/data.csv") # Relative Path for the Data For Now
    matches = matcher.match() # Returns a dictionary of matches

    return jsonify(matches)

if __name__ == "__main__":
    app.run()