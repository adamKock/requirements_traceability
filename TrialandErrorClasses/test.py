import pandas as pd
from sentence_transformers import SentenceTransformer, util
import csv

#Load Pre trained model 
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Mock Data from a csv for business requirements
rf = pd.read_csv("Business_Requirements_Test.csv")
print(rf.columns.tolist())

#2 Mock business requirement from csv
business_requirement = rf['Requirement ']
print(business_requirement)

#3 Mock test case from csv
tf= pd.read_csv("Test_Cases.csv")
print(tf.columns.tolist())
test_requirement = tf['Test Case Description ']
print(test_requirement)


# 4 Comparison Logic 
print("--- Traceability Gap Analysis ---")



