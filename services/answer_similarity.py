
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load preprocessed dataset
df = pd.read_parquet(
    "dataset/processed/asag2024_preprocessed.parquet"
)

# Select student and reference answers
student_answers = df["processed_answer"].fillna("")
reference_answers = df["processed_reference"].fillna("")

# Create a common vocabulary
all_answers = pd.concat(
    [student_answers, reference_answers],
    ignore_index=True
)

# Initialize TF-IDF
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2)
)

# Fit vectorizer on both types of answers
tfidf_matrix = vectorizer.fit_transform(all_answers)

# Split student and reference matrices
n = len(df)

student_matrix = tfidf_matrix[:n]
reference_matrix = tfidf_matrix[n:]

# Calculate cosine similarity for corresponding pairs
similarity_scores = []

for i in range(n):
    score = cosine_similarity(
        student_matrix[i],
        reference_matrix[i]
    )[0][0]

    similarity_scores.append(score)

# Save similarity scores
df["tfidf_similarity"] = similarity_scores

# Display sample results
print("ANSWER SIMILARITY RESULTS")

for i in range(5):
    print("\nRecord:", i + 1)
    print("Student Answer:", df["provided_answer"].iloc[i])
    print("Reference Answer:", df["reference_answer"].iloc[i])
    print("Actual Normalized Grade:", df["normalized_grade"].iloc[i])
    print(
        "TF-IDF Similarity:",
        round(df["tfidf_similarity"].iloc[i], 4)
    )

# Save results
df.to_parquet(
    "dataset/processed/asag2024_similarity.parquet",
    index=False
)

print("\nSimilarity calculation completed!")
print("Total records:", len(df))
