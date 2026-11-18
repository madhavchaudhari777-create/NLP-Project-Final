
import pandas as pd

df = pd.read_parquet("dataset/asag2024/train.parquet")

print("TOTAL RECORDS:", len(df))

# Check duplicate records
duplicates = df[df.duplicated(keep=False)]

print("\nDUPLICATE ROWS:", len(duplicates))
print("\nSample duplicate records:")
print(duplicates.head(4).to_string(index=False))

# Check missing questions
missing_questions = df[df["question"].isna()]

print("\nMISSING QUESTIONS:", len(missing_questions))

# Check missing student answers
missing_answers = df[df["provided_answer"].isna()]

print("\nMISSING STUDENT ANSWERS:", len(missing_answers))

# Check normalized grade range
print("\nNORMALIZED GRADE MIN:", df["normalized_grade"].min())
print("NORMALIZED GRADE MAX:", df["normalized_grade"].max())

# Check empty text values
print("\nEMPTY STUDENT ANSWERS:")
print((df["provided_answer"].fillna("").str.strip() == "").sum())