import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import textwrap

# 1. Load data
test_data_set = pd.read_csv("Traceability_Results.csv")

# 2. Improve the Labels: Text wrapping for the Y-axis
# This prevents the labels from pushing the chart off the screen
test_data_set['Requirement_Wrapped'] = test_data_set['Requirement'].apply(
    lambda x: "\n".join(textwrap.wrap(x, width=40))
)

# 3. Setup the Figure Size
# Horizontal plots benefit from being taller
plt.figure(figsize=(12, 8))

# 4. Apply Theme and Plot
sns.set_theme(style="whitegrid")
ax = sns.barplot(
    data=test_data_set, 
    x="Count of testcases that meet threshold", 
    y="Requirement_Wrapped", 
    hue="Requirement_Wrapped",
    palette="viridis",
    legend=False  # Removes the redundant legend since Requirement is already on the Y axis
)

# 5. Centering and Formatting
plt.title("Test Case Coverage per Requirement", fontsize=16, pad=20)
plt.xlabel("Number of Test Cases Meeting Threshold", fontsize=12)
plt.ylabel("Business Requirement", fontsize=12)

# Ensure the integers on the X-axis don't show decimals (like 1.5)
from matplotlib.ticker import MaxNLocator
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

# 6. The "Magic" Layout Fix
plt.tight_layout()

plt.show()