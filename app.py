### TO DO: Flask app

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from interview.main import InterviewAgent
from interview.agents.utils import Termination
from match.matcher import Matcher
import json
import os

load_dotenv()
app = Flask(__name__)
interview_agent = InterviewAgent("John Doe", os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"))

@app.route('/')
def home() -> None:
    return render_template('index.html')

@app.route('/get_response', methods = ["POST"])
def get_response() -> json:
    message = request.form["message"]
    response = interview_agent.get_response(message)
    return jsonify({"question": response})

@app.route('/get_match', methods = ["GET"])
def get_match() -> json:
    user_attributes = interview_agent.terminate_interview()
    matcher = Matcher(user_attributes, "match/data.csv") # Relative Path for the Data For Now
    matches = matcher.match() # Returns a dictionary of matches
    print(matches)

    return jsonify(matches)

if __name__ == "__main__":
    app.run()