
import pandas as pd

df = pd.read_parquet("dataset/asag2024/train.parquet")

# Count exact duplicate rows
exact_duplicates = df.duplicated().sum()

# Count duplicate groups using question, answer and reference answer
text_columns = [
    "question",
    "provided_answer",
    "reference_answer"
]

text_duplicates = df.duplicated(
    subset=text_columns
).sum()

# Count duplicates including their grades and sources
grading_columns = [
    "question",
    "provided_answer",
    "reference_answer",
    "normalized_grade"
]

grading_duplicates = df.duplicated(
    subset=grading_columns
).sum()

print("EXACT DUPLICATE ROWS:", exact_duplicates)
print("DUPLICATES BASED ON TEXT:", text_duplicates)
print("DUPLICATES INCLUDING NORMALIZED GRADE:", grading_duplicates)

# Show examples of repeated text with different grades
repeated = df[
    df.duplicated(subset=text_columns, keep=False)
]

print("\nSAMPLE REPEATED TEXT RECORDS:")
print(
    repeated[
        text_columns + ["normalized_grade", "data_source"]
    ].head(10).to_string(index=False)
)