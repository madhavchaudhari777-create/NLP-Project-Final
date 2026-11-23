
import pandas as pd
from scipy.stats import pearsonr, spearmanr

# Load similarity dataset
df = pd.read_parquet(
    "dataset/processed/asag2024_similarity.parquet"
)

# Select relevant columns
data = df[
    ["tfidf_similarity", "normalized_grade"]
].dropna()

similarity = data["tfidf_similarity"]
grades = data["normalized_grade"]

# Calculate correlations
pearson_corr, pearson_p = pearsonr(similarity, grades)

spearman_corr, spearman_p = spearmanr(similarity, grades)

print("TF-IDF SIMILARITY EVALUATION")

print("\nTotal records:", len(data))

print("\nPearson Correlation:", round(pearson_corr, 4))
print("Pearson P-value:", pearson_p)

print("\nSpearman Correlation:", round(spearman_corr, 4))
print("Spearman P-value:", spearman_p)

# Compare average similarity by grade
print("\nAVERAGE SIMILARITY BY GRADE")

print(
    data.groupby("normalized_grade")["tfidf_similarity"]
    .mean()
    .round(4)
    .head(15)
)

print("\nEvaluation completed!")
