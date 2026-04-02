import torch

# Example requirements
req_texts = [
    "User can login",
    "User can reset password",
    "Admin can delete account"
]

# Example test cases
test_cases = [
    "Verify login works with valid credentials",
    "Check password reset email is sent",
    "Ensure admin can remove a user",
    "Test login fails with wrong password"
]

similarity = torch.tensor([
    [0.80, 0.10, 0.05, 0.75],
    [0.20, 0.85, 0.10, 0.15],
    [0.05, 0.05, 0.90, 0.10]
])

threshold = 0.7

rows, cols = (similarity > threshold).nonzero(as_tuple=True)

matches_table = torch.stack(
    [rows, cols, similarity[rows, cols]],
    dim=1
)

print("Matches Table:")
print(matches_table)

print("\nDecoded Matches:\n")

for row, col, score in matches_table:
    row = int(row)
    col = int(col)

    print(f"Requirement: {req_texts[row]}")
    print(f"Test Case:  {test_cases[col]}")
    print(f"Score:      {score:.4f}")
    print("-" * 50)

from collections import defaultdict

grouped = defaultdict(list)

for row, col, score in matches_table:
    grouped[int(row)].append((int(col), float(score)))

print("\nGrouped Output:\n")

for row, matches in grouped.items():
    print(f"Requirement: {req_texts[row]}")
    for col, score in matches:
        print(f"   → {test_cases[col]} ({score:.4f})")
    print("-" * 50)