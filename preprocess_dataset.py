
import pandas as pd
import os

# Load original dataset
input_path = "dataset/asag2024/train.parquet"
df = pd.read_parquet(input_path)

print("ORIGINAL DATASET:", df.shape)

# Step 1: Remove records with missing question or student answer
df_clean = df.dropna(
    subset=["question", "provided_answer"]
).copy()

print("AFTER REMOVING MISSING TEXT:", df_clean.shape)

# Step 2: Remove empty question or answer strings
df_clean = df_clean[
    (df_clean["question"].str.strip() != "") &
    (df_clean["provided_answer"].str.strip() != "")
].copy()

print("AFTER REMOVING EMPTY TEXT:", df_clean.shape)

# Step 3: Remove exact duplicate rows
df_clean = df_clean.drop_duplicates().copy()

print("AFTER REMOVING EXACT DUPLICATES:", df_clean.shape)

# Step 4: Save cleaned dataset
output_dir = "dataset/processed"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(
    output_dir,
    "asag2024_cleaned.parquet"
)

df_clean.to_parquet(output_path, index=False)

print("\nCLEANED DATASET SAVED SUCCESSFULLY!")
print("Location:", output_path)

# Final validation
print("\nFINAL MISSING VALUES:")
print(df_clean.isnull().sum())

print("\nFINAL DATASET SHAPE:", df_clean.shape)
