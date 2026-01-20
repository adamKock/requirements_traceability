import pandas as pd
from sentence_transformers import SentenceTransformer, util
import csv

# 1. Load the "Intelligence" (Pre-trained model)
# This model understands that "Login" and "Sign-in" are the same thing.
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Mock Data (In your PoC, this would be your BRD and SpiraTeam CSV)
requirements = [
    "The system shall allow users to reset their passwords via email.",
    "User must be able to export reports in PDF format.",
    "The application should support biometric authentication."
]

test_cases = [
    "Verify password reset functionality",
    "Check PDF export for monthly reports",
    "Validate login with username and password", # Note: This doesn't match well
    "Ensure fingerprint scanner works for login"
]

from sentence_transformers import SentenceTransformer

# Load https://huggingface.co/sentence-transformers/all-mpnet-base-v2
model = SentenceTransformer("all-mpnet-base-v2")
embeddings = model.encode([
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
])
similarities = model.similarity(embeddings, embeddings)
print(similarities)

# 3. The "Matching" Logic
print("--- Traceability Gap Analysis ---")

for req in requirements:
    # Encode the requirement and all test cases into "vectors"
    req_vec = model.encode(req, convert_to_tensor=True)
    test_vecs = model.encode(test_cases, convert_to_tensor=True)
    
    # Compute Cosine Similarity (The "Similarity Score")
    cosine_scores = util.cos_sim(req_vec, test_vecs)[0]
    
    # Find the best match
    best_score_idx = cosine_scores.argmax()
    best_score = cosine_scores[best_score_idx].item()
    
    print(f"\nRequirement: {req}")
    if best_score > 0.5: # 0.5 is a standard 'decent match' threshold
        print(f"Best Test Match: '{test_cases[best_score_idx]}' (Score: {best_score:.2f})")
    else:
        print("⚠️ NO MATCH FOUND - COVERAGE GAP DETECTED")