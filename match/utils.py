# Preprocessing
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from typing import Any, List
import torch

MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def obtain_tensors_dataframe(dataset: pd.DataFrame) -> List[torch.Tensor]:
    """Get a dataset and obtain a list of tensors for each row in the dataset.

    Attributes:
        dataset: The current csv dataset.
    """

    test = dataset.T.to_dict('list')
    test_names = []

    for name in test:
        curr_name = MODEL.encode(test[name])
        test_names.append(curr_name)
    
    return test_names

def obtain_tensors_list(dataset: List[str]) -> torch.Tensor:
    """Get a tensors for an entire list.
    
    Attributes:
        - dataset: The list of strings to be converted into one tensor.
    """

    return MODEL.encode(dataset)

def calculate_cosine(candidate_data: List[str], profiles_list: pd.DataFrame, profile_tensors: List[torch.Tensor]) -> pd.DataFrame:
    """Calculate the cosine and return the highest matches of the profiles.
    
    Attributes:
        - candidate_data: The current company data in 
        - profiles_list: The list of tensors from th
        - profile_tensors: The list of tensors
    """

    all_talent_embedding = []

    for curr_name in profile_tensors:
        cosine = cosine_similarity(candidate_data, curr_name).mean(axis = 1).mean()
        all_talent_embedding.append(cosine)
    
    profiles_list["Cosine"] = all_talent_embedding

    return profiles_list

def filter(profiles_list: pd.DataFrame, column: str, filter: str) -> pd.DataFrame:
    """Filter the dataframe."""

    new = profiles_list[profiles_list[column] == filter]

    return new