
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
import os

# Load preprocessed dataset
df = pd.read_parquet(
    "dataset/processed/asag2024_preprocessed.parquet"
)

# Prepare student answer text
answers = df["processed_answer"].fillna("")

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2)
)

# Convert text into numerical features
tfidf_matrix = vectorizer.fit_transform(answers)

# Display results
print("TF-IDF VECTORIZATION COMPLETED")

print("\nNumber of records:", tfidf_matrix.shape[0])
print("Number of features:", tfidf_matrix.shape[1])

print("\nFirst 20 vocabulary terms:")
print(vectorizer.get_feature_names_out()[:20])

print("\nFirst answer:")
print(answers.iloc[0])

print("\nTF-IDF values for first answer:")
print(tfidf_matrix[0].toarray())

# Create output directory
os.makedirs("dataset/vectorized", exist_ok=True)

# Save vectorizer
joblib.dump(
    vectorizer,
    "dataset/vectorized/tfidf_vectorizer.pkl"
)

# Save sparse TF-IDF matrix
save_npz(
    "dataset/vectorized/answers_tfidf.npz",
    tfidf_matrix
)

print("\nVectorizer and TF-IDF matrix saved successfully!")
