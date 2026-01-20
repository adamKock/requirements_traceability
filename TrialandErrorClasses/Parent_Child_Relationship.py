from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap

capitals = [
    {"USA" : "Washington DC", 
     "Population" : 69, 
     "Main Language": "English "}, 

      {"UK" : "London ", 
     "Population" : 20, 
     "Main Language": "English "}, 

]

#How to go into a list of dicts and get a value from the key value pair 
print(capitals[1]["UK"])

requirements = [
    {"id": 1, "summary": "Login"},
    {"id": 2, "summary": "Checkout"},
    {"id": 3, "summary": "Search"},
]

test_cases = [
    {"id": 101, "summary": "Valid login", "requirement_id": 1},
    {"id": 102, "summary": "Invalid login", "requirement_id": 1},
    {"id": 201, "summary": "Add to cart", "requirement_id": 2},
    {"id": 202, "summary": "Payment failure", "requirement_id": 2},
]
 

business_requirements = pd.read_csv("Business_Requirements_Ver_Two.csv").to_dict('records')
test_cases_csv = pd.read_csv("Test_Cases_Ver_Two.csv").to_dict('records')
print("Available columns in Test Cases:", test_cases_csv[0].keys())
print("Available columns in Test Cases:", business_requirements[0].keys())
traceability_matrix =[]

#What we need to do is iterate through the list of requirements. 
#Then iterate through the list of test cases and look for matches then if there is a match add tha to match requirements
for requirment in business_requirements:
    match_requirements = []
   # Instead of checking the whole list, check each case one by one
    for case in test_cases_csv: 
        if case["Requirement ID"] == requirment["ID"]:
           match_requirements.append(case)


    requirement_folder = {
        "id": requirment["ID"],
        "summary": requirment["Requirement"],
        "test_cases": match_requirements

    }
    traceability_matrix.append(requirement_folder)


print(traceability_matrix)


model = SentenceTransformer("all-mpnet-base-v2")

for req_entry in traceability_matrix:
    req_text = req_entry["summary"]
    test_case_list = req_entry["test_cases"]

    if not test_case_list:
        print(f"REQ-{req_entry['id']}: Skipped (No test cases to audit)")
        continue
    
    req_embeding = model.encode(req_text, convert_to_tensor=True)

    test_case_text = [tc["Test Case Description"] for tc in test_case_list]
    tc_embeddings = model.encode(test_case_text, convert_to_tensor=True)

    scores = util.cos_sim(req_embeding, tc_embeddings)[0]

    print(f"\nAudit for {req_entry['id']} ({req_text[:100]}):")

    for i, score in enumerate(scores):
        val = score.item()
        test_case_list[i]["ai_confidence"] = round(val, 2)
        
        status = "Strong" if val > 0.6 else "Weak"
        print(f"  --> TC-{test_case_list[i]['TC ID']}: {status} match ({val:.2f})")





