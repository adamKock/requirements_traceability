from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap


#This looks at 3 different matrixes 
# Requirment vs Test Case Steps":
#"Requirement vs Test Case Summary"
#"Test Case Summary vs Test Steps"
    

##List the requirments 
#Then do the multi layered dict
#Create list
#Then iterate through the test cases and the steps per requirement ?



#Create blank list
#Outer For loop going through the requirements
#Inner For loop going through each of the test cases and seeing if it matches the requirement ID 
# If it matches the ID then loop through the steps and then add each test case and the steps into the matched requirements 
#Need to create a dict data type and then add that to a list created outside the loop
requirements = [
    {"id": 1, "summary": "Login"},
    {"id": 2, "summary": "Checkout"},
    {"id": 3, "summary": "Search"},
]


mld_test_cases=[{
    "id":101,
    "summary":"Validate Login",
    "requirement_id":1,
    "test_steps":[
            {"step_num": 1, "action": "Click forgot password"},
            {"step_num": 2, "action": "Check inbox for link"},
            {"step_num": 3, "action": "Click reset URL"} 
        
    ]
    }, 
    {
    "id":102,
    "summary":"Invalid Login",
    "requirement_id":2,
    "test_steps":[
        {"step_num": 1, "action": "Enter wrong password"},
        {"step_num": 2, "action": "Click login"},
        {"step_num": 3, "action": "Verify error message"}
    ]

    }
]
traceability_matrix =[]

for requirement in requirements:
    match_requirments =[]

    for case in mld_test_cases:
        if case["requirement_id"] == requirement["id"]:
            full_procedure = " ".join([step['action'] for step in case['test_steps']])
            case["combined_procedure"] = full_procedure
            match_requirments.append(case)
    
    requirement_folder = {
        "id": requirement["id"],
        "summary": requirement["summary"],
        "test_cases": match_requirments

    }
    traceability_matrix.append(requirement_folder)

print(f"Joined Steps for REQ-{traceability_matrix[0]['id']}:")
print(traceability_matrix[0]['test_cases'][0]['combined_procedure'])


model = SentenceTransformer("all-mpnet-base-v2")

for req_entry in traceability_matrix:
    req_text = req_entry["summary"]
    test_case_list = req_entry["test_cases"]

    if not test_case_list:
        print(f"REQ-{req_entry['id']}: Skipped (No test cases to audit)")
        continue

    req_embedding = model.encode(req_text, convert_to_tensor=True)

    for case in test_case_list:
        test_steps = case.get("combined_procedure")
        case_summary_text = case.get("summary")
        if not test_steps:
            print(f"  --> TC-{case['id']}: Skipped (No steps)")
            continue


        req_emb = req_embedding 
        summary_emb = model.encode(case_summary_text, convert_to_tensor=True)
        steps_emb = model.encode(test_steps, convert_to_tensor=True)

        score_steps_req = util.cos_sim(req_emb, steps_emb)[0].item()
        score_summary_req = util.cos_sim(req_emb, summary_emb)[0].item()
        score_steps_summary = util.cos_sim(summary_emb, steps_emb)[0].item()
        
    case["audit_scores"] = {
        "Requirment vs Test Case Steps":round(score_steps_req, 2),
        "Requirement vs Test Case Summary":round(score_summary_req, 2),
        "Test Case Summary vs Test Steps":round(score_steps_summary, 2)
    }

    print(f"  --> TC-{case['id']} Audit:")
    print(f"      - Requirment vs Test Case Steps: {score_steps_req:.2f}")
    print(f"      - Requirement vs Test Case Summary: {score_summary_req:.2f}")
    print(f"      - Test Case Summary vs Test Steps: {score_steps_summary:.2f}")
    
    

print(traceability_matrix)
   




