
import pandas as pd
from services.text_preprocessing import preprocess_text

# Load cleaned dataset
df = pd.read_parquet(
    "dataset/processed/asag2024_cleaned.parquet"
)

print("Original dataset shape:", df.shape)

# Apply preprocessing
df["processed_question"] = df["question"].apply(preprocess_text)

df["processed_answer"] = df["provided_answer"].apply(preprocess_text)

df["processed_reference"] = df["reference_answer"].apply(preprocess_text)

# Display sample results
print("\nPREPROCESSING RESULTS")

for i in range(3):
    print("\nRecord:", i + 1)
    print("Original Answer:", df["provided_answer"].iloc[i])
    print("Processed Answer:", df["processed_answer"].iloc[i])
    print("Reference Answer:", df["reference_answer"].iloc[i])
    print("Processed Reference:", df["processed_reference"].iloc[i])

# Save processed dataset
output_path = "dataset/processed/asag2024_preprocessed.parquet"

df.to_parquet(output_path, index=False)

print("\nPreprocessing completed successfully!")
print("Final dataset shape:", df.shape)
print("Saved at:", output_path)
