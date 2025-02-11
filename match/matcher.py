"""
This is the Matcher class which attempts to match the results from the interview to companies or candidates.

Key Features:
    - Fetch data from a vector database (PineCone) - Not Implemented Yet
        - In its' current iteration, this will simply use the Cosine Similarity.
    - Output the match 

This class will take in a dataset, currently in csv format.
"""

import logging
from match.utils import *
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from typing import Any, Dict


class Matcher:
    """
    The Matcher class which aims to match people with their values.

    Attributes:
        - dataset: The csv filepath. Must contain the subfield: values_summary
        - user_attributes: The user attributes obtained from the interview.
        - tensors: The Tensors in the csv file.
        - model: The Sentence Transformer model for cosine calculation.
    
    Pre Condition: self.dataset must have:
        - id: ID of the interview
        - name: Name of the interviewee
        - time: The current time
        - question_answer: Question Answer history
        - impression: The impression by the agent
    """

    def __init__(self, user_attributes: Dict, csv_file: str) -> None:
        """Initialize the Matcher class.

        Attributes:
        - csv_file: The csv filepath. Must contain the subfield: values_summary
        - user_attributes: The user attributes obtained from the interview.
        """

        self.user_attributes = user_attributes
        self.dataset = pd.read_csv(csv_file, on_bad_lines = "skip", index_col = False)
        self.tensors = obtain_tensors_dataframe(self.dataset)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def match(self, maximum_count: int = 2) -> Dict:
        """Conduct value matching by calculating the Cosine Similarity.
        
        Pre Condition: self.user_attributes must have:
            - id: ID of the interview
            - name: Name of the interviewee
            - time: The current time
            - question_answer: Question Answer history
            - impression: The impression by the agent
        """

        print(self.user_attributes)
        candidate_values = obtain_tensors_list([self.user_attributes["impression"]]) # Values Deduction: Must be a list and calculates the impression!
        cosine_dataframe = calculate_cosine(candidate_values, self.dataset, self.tensors)
        cosine_dataframe = cosine_dataframe.sort_values(by=["Cosine"], ascending = False)
        print(cosine_dataframe)
        cosine_dataframe = cosine_dataframe.iloc[:maximum_count]

        return cosine_dataframe.to_dict('records')