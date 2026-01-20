from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap

# Load https://huggingface.co/sentence-transformers/all-mpnet-base-v2 - Model selected 
model = SentenceTransformer("all-mpnet-base-v2")

br = pd.read_csv("Business_Requirements_Test.csv")
business_requirements = br['Requirement'].tolist()

tc = pd.read_csv("Test_Cases.csv")
test_cases = tc['Test Case Description'].tolist()


# Threshold of confidence 
threshold = 0.35

# Encoding the requirements and test case list putting it into tensor data 
requirements_sentc = model.encode(business_requirements)
test_cases_sentc = model.encode(test_cases)

# What this does is that it takes the requirements and then looks at all the test cases and then scores them based on similarity. Higher the number the higher the confidence. 
# It creates a 2Dimension array the rows are the requirements and columns are the test cases with the confidence scores inside 
# It uses the tesnor data from the model encode above 
similairty = util.cos_sim(requirements_sentc, test_cases_sentc)  



print("Requirement Tensor Data")
print(requirements_sentc)
print("Test Case Data")
print(test_cases_sentc)

print(f"{'Requirement':<60} | {'Best Test Match':<40} | {'Score'}")
print("-" * 120)

results_data = []

#Outer For loop
for i, req in enumerate(business_requirements):
    # Creates a var called row scores which takes the score of the whole row and the individual test cases. The row being the first index of the requirements list
    row_scores = similairty[i]
    # What this does is we create a new list called match indicies and that is the outcome of the for loop 
    # It loops through all the columns in the row and sees if the row score is greater than our threshold if it is then put the index of it into a new list calld match_index 
    # EG if a test case that beats threshold the index goes into the list 
    match_indices = [idx for idx, score in enumerate(row_scores) if score >=threshold]

    # Then we take the list and sort the list into highest confidence to lowest for the ones that met the threshold 
    match_indices = sorted(match_indices, key=lambda x:row_scores[x], reverse=True)

    #If match indices at the index has a blank list aka no matches then update status of that index to a GAP 
    if not match_indices:
        status = "GAP"
        print(f"{req[:58]:<60} | {status:<10} | No matches found.")
    # Else if the list is not blank then update the status to mapped if the first row score is greater than o.6( as it's been sorted) confidence else put review which outlines it found something but might not be 100%
    else:
        status = "Mapped" if row_scores[match_indices[0]] >0.6 else "Review"

        print(f"{req[:58]:<60} | {status:<10}")

    results_data.append({
        "Requirement":req,
        "Status":status,
        "Top Match": "None" if not match_indices else test_cases[match_indices[0]],
        "Count of testcases that meet threshold": len(match_indices) if match_indices else 0
    })


        #Inner for loop
        # For loop on match_indices that loops through the test cases and their index that match
    for idx in match_indices:
        # We create new var which is the actual test case text and = to test cases at the index[idx]
        test_case_text = test_cases[idx]
        # create score and = to row scores index [idx] we use.item() method to get the confidence value of the index on the row
        score = row_scores[idx].item() 
        print(f"{'':<60} | {'':<10} | --> {test_case_text} ({score:.2f})")
            
    print("-" * 120)

output_df = pd.DataFrame(results_data)
output_df.to_csv("Traceability_Results.csv", index=False)
print("Export Completed")

# Load data
test_data_set = pd.read_csv("Traceability_Results.csv")

# Improve the Labels: Text wrapping for the Y-axis
# This prevents the labels from pushing the chart off the screen
# How this works - it creates a new column alled Requirementwrapped and = it to requirement
# We use. apply function (higher order) that takes another function as a param
# We use lamda as that param and in the lambda function we use x as the requirement in requirements column 
# Inside .join (function that requires param)We use text.wrap.wrap x, 40 to split the requirement into a list with different indexs every 40chars
# Once the split has worked that returns the list the join is executed joining indexes back together but the second index being on a new line 
test_data_set['Requirement_Wrapped'] = test_data_set['Requirement'].apply(
    lambda x: "\n".join(textwrap.wrap(x, width=40))
)

# Define colors for statuses 
status_colors = {"Mapped": "green", "Review": "orange", "GAP": "red"}

# Setup the Figure Size
# Horizontal plots change
plt.figure(figsize=(12, 8))

# Apply Theme and Plot
sns.set_theme(style="whitegrid")
ax = sns.barplot(
    data=test_data_set, 
    x="Count of testcases that meet threshold", 
    y="Requirement_Wrapped", 
    hue="Status",
    palette=status_colors,
    legend=False  # Removes the redundant legend since Requirement is already on the Y axis
)

# Centering and Formatting
plt.title("Test Case Coverage per Requirement", fontsize=16, pad=20)
plt.xlabel("Number of Test Cases Meeting Threshold", fontsize=12)
plt.ylabel("Business Requirement", fontsize=12)

# Ensure the integers on the X-axis don't show decimals (like 1.5)
from matplotlib.ticker import MaxNLocator
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

for container in ax.containers:
    ax.bar_label(container, padding=3)
plt.tight_layout()
plt.show()

total = len(test_data_set)
mapped = len(test_data_set[test_data_set['Status'] == 'Mapped'])
gaps = len(test_data_set[test_data_set['Status'] == 'GAP'])
review = len(test_data_set[test_data_set['Status'] == 'Review'])

print("\n" + "="*30)
print(f"TRACEABILITY SUMMARY")
print(f"Total Requirements: {total}")
print(f"Fully Mapped:      {mapped} ({mapped/total:.1%})")
print(f"Needs Review: {review} ({review/total:.1%})")
print(f"Identified GAPs:   {gaps} ({gaps/total:.1%})")
print("="*30)


# Next steps 
# Already have a joined csv that has both the requirements and also the pre defined test cases that are linked to the requirement
# Then load the CSV in and check how confident are we that those test cases cover the requirement

#To do above 









#Side Quest
#Widget to take the requirements document and upload them all into SpiraTeam