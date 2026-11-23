
import pandas as pd

df = pd.read_parquet("dataset/asag2024/train.parquet")

print("GRADE DISTRIBUTION")
print(df["grade"].value_counts().sort_index())

print("\nNORMALIZED GRADE DISTRIBUTION")
print(df["normalized_grade"].value_counts().sort_index())

print("\nDATA SOURCE DISTRIBUTION")
print(df["data_source"].value_counts())

print("\nDUPLICATE RECORDS")
print(df.duplicated().sum())

print("\nANSWER LENGTHS")
print("Average student answer length:",
      df["provided_answer"].dropna().str.len().mean())

print("Average reference answer length:",
      df["reference_answer"].str.len().mean())
