
import pandas as pd

df = pd.read_parquet("dataset/asag2024/train.parquet")

text_columns = [
    "question",
    "provided_answer",
    "reference_answer"
]

# Ignore records with missing text for this analysis
valid = df.dropna(subset=text_columns).copy()

# Find repeated text combinations with different normalized grades
grade_counts = (
    valid.groupby(text_columns, dropna=False)["normalized_grade"]
    .nunique()
)

conflicting_groups = grade_counts[grade_counts > 1]

print("TOTAL REPEATED TEXT GROUPS:",
      (grade_counts > 1).sum() + (grade_counts == 1).sum()
      - (grade_counts == 1).sum())

print("\nTEXT GROUPS WITH DIFFERENT GRADES:",
      len(conflicting_groups))

if len(conflicting_groups) > 0:
    conflict_data = valid.merge(
        conflicting_groups.rename("grade_count").reset_index(),
        on=text_columns
    )

    print("\nSAMPLE CONFLICTING RECORDS:")
    print(
        conflict_data[
            text_columns + ["normalized_grade", "data_source"]
        ].head(10).to_string(index=False)
    )
else:
    print("\nNo conflicting grades found.")