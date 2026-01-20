# Import seaborn
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


# Apply the default theme
sns.set_theme()





test_data_set = pd.read_csv("Traceability_Results.csv")
sns.barplot(data=test_data_set, x="Count of testcases that meet threshold", y="Requirement", hue="Requirement")
plt.tight_layout()
plt.xticks(rotation=0, ha='center')
plt.show()


