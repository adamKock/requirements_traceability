from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/stsb-roberta-base")

labeled_pairs = [
    # --- existing ones ---
    ("Users must be able to see the weather for all places where we have an office",
     "View weather for office locations", "excellent"),
    ("Users must be able to reset passwords using a self service reset function",
     "Reset password using email link", "good"),
    ("Applications must support fingerprint as well as face scanning for authentication",
     "Login using facial recognition", "good"),
    ("Users must be able to reset passwords using a self service reset function",
     "Export financial report as PDF", "bad"),

    # --- more clear "excellent" matches ---
    ("Users must be able to export reports as PDFs using a self service mechanism",
     "Export sales report to PDF", "excellent"),
    ("System must lock user accounts after 5 failed login attempts",
     "Verify account lockout after 5 failed login attempts", "excellent"),
    ("Users must receive an email confirmation after submitting an order",
     "Verify order confirmation email is sent", "excellent"),

    # --- more clear "good" matches (related but not exact wording) ---
    ("Applications must support fingerprint as well as face scanning for authentication",
     "Login using fingerprint authentication", "good"),
    ("Users must be able to update their profile information",
     "Edit user profile name and email", "good"),
    ("System must support multi-factor authentication for admin accounts",
     "Verify 2FA prompt appears for admin login", "good"),

    # --- borderline / uncertain matches ---
    ("Users must be able to reset passwords using a self service reset function",
     "Admin resets a user's password on their behalf", "borderline"),
    ("Applications must support fingerprint as well as face scanning for authentication",
     "Login using username and password", "borderline"),
    ("Users must be able to export reports as PDFs using a self service mechanism",
     "Export report data as CSV", "borderline"),
    ("System must lock user accounts after 5 failed login attempts",
     "Verify password strength requirements on signup", "borderline"),

    # --- more clear "bad" matches (unrelated domains) ---
    ("Users must be able to see the weather for all places where we have an office",
     "Verify account lockout after 5 failed login attempts", "bad"),
    ("Applications must support fingerprint as well as face scanning for authentication",
     "Export sales report to PDF", "bad"),
    ("System must lock user accounts after 5 failed login attempts",
     "View weather for office locations", "bad"),
    ("Users must receive an email confirmation after submitting an order",
     "Login using fingerprint authentication", "bad"),
]

pairs = [(req, tc) for req, tc, _ in labeled_pairs]
scores = reranker.predict(pairs)

for (req, tc, label), score in sorted(zip(labeled_pairs, scores), key=lambda x: x[1], reverse=True):
    print(f"{score:.3f}  [{label:10}]  {req[:50]}  <->  {tc[:50]}")