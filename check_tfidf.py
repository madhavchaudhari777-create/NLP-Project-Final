
import pandas as pd
import joblib
from scipy.sparse import load_npz

# Load saved data
df = pd.read_parquet(
    "dataset/processed/asag2024_preprocessed.parquet"
)

vectorizer = joblib.load(
    "dataset/vectorized/tfidf_vectorizer.pkl"
)

matrix = load_npz(
    "dataset/vectorized/answers_tfidf.npz"
)

# Inspect first answer
print("FIRST PROCESSED ANSWER:")
print(df["processed_answer"].iloc[0])

print("\nNON-ZERO TF-IDF FEATURES:")

row = matrix[0]
feature_names = vectorizer.get_feature_names_out()

for index, value in zip(row.indices, row.data):
    print(feature_names[index], ":", round(float(value), 4))

print("\nMATRIX INFORMATION")
print("Shape:", matrix.shape)
print("Non-zero values:", matrix.nnz)
print("Sparsity:", round(
    100 * (1 - matrix.nnz / (matrix.shape[0] * matrix.shape[1])), 2
), "%")
