"""
RoadSense.ai - Task 4: Data Analytics

Creates dataset quality reports, separates estimated records,
and produces a review list for district-level data.

Existing status labels are not independent proof of accuracy.
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent

INPUT_FILE = (
    BASE_DIR
    / "RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv"
)

df = pd.read_csv(INPUT_FILE)

# Convert numeric fields safely.
numeric_columns = ["Year", "Accident Cases", "Injured", "Died"]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

status = df["Data Status"].fillna("").astype(str).str.strip()
source = df["Source"].fillna("").astype(str).str.strip()
state = df["State/UT"].fillna("").astype(str).str.strip()

is_state_total = status.str.contains(
    "Official State/UT data", case=False, regex=False
)

is_estimated = status.str.contains(
    "Estimated", case=False, regex=False
)

is_labelled_verified = status.str.contains(
    "Verified", case=False, regex=False
)

# These are source-review categories, not automatic proof of verification.
is_tamil_nadu = state.str.casefold().eq("tamil nadu")
is_haryana = state.str.casefold().eq("haryana")

has_tn_source_name = source.str.contains(
    "Tamil Nadu Transport Department",
    case=False,
    regex=False
)

has_haryana_source_name = source.str.contains(
    "Statistical Abstract of Haryana",
    case=False,
    regex=False
)

# 1. Dataset quality summary.
summary = pd.DataFrame({
    "Metric": [
        "Dataset rows",
        "Distinct State/UT labels",
        "Distinct district names",
        "Missing accident cases",
        "Missing injured values",
        "Missing deaths",
        "Exact duplicate rows",
        "Records labelled Official State/UT data",
        "Records labelled Estimated",
        "Records labelled Verified",
        "Tamil Nadu records",
        "Tamil Nadu records naming the department as source",
        "Haryana records",
        "Haryana records naming the Statistical Abstract as source",
    ],
    "Value": [
        len(df),
        df["State/UT"].nunique(),
        df["District"].nunique(),
        df["Accident Cases"].isna().sum(),
        df["Injured"].isna().sum(),
        df["Died"].isna().sum(),
        df.duplicated().sum(),
        int(is_state_total.sum()),
        int(is_estimated.sum()),
        int(is_labelled_verified.sum()),
        int(is_tamil_nadu.sum()),
        int((is_tamil_nadu & has_tn_source_name).sum()),
        int(is_haryana.sum()),
        int((is_haryana & has_haryana_source_name).sum()),
    ]
})

summary.to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_Data_Quality_Summary.csv",
    index=False
)

# 2. Counts for each existing data-status label.
status_counts = (
    df["Data Status"]
    .fillna("Missing status")
    .value_counts()
    .rename_axis("Data Status")
    .reset_index(name="Record Count")
)

status_counts.to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_Data_Status_Counts.csv",
    index=False
)

# 3. Number of dataset records per State/UT.
state_counts = (
    df.groupby("State/UT", dropna=False)
    .size()
    .reset_index(name="Dataset Records")
    .sort_values("Dataset Records", ascending=False)
)

state_counts.to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_District_Record_Counts_by_State.csv",
    index=False
)

# 4. Create a source-review file for district records.
# No record is declared independently verified by this script.
review = df[
    [
        "Year",
        "State/UT",
        "District",
        "Accident Cases",
        "Injured",
        "Died",
        "Data Status",
        "Source",
    ]
].copy()

review["Review Outcome"] = "Needs source verification"

review.loc[
    is_estimated,
    "Review Outcome"
] = "Estimated - do not present as verified district data"

review.loc[
    is_state_total,
    "Review Outcome"
] = "State/UT-labelled record - check geographic level"

review.loc[
    is_tamil_nadu & has_tn_source_name,
    "Review Outcome"
] = (
    "Tamil Nadu source named - verify each metric against the report"
)

review.loc[
    is_haryana & has_haryana_source_name,
    "Review Outcome"
] = (
    "Haryana source named - verify each metric against Table 22.3"
)

review.to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_Source_Verification_Review.csv",
    index=False
)

# 5. Keep estimated records in a separate file.
df.loc[is_estimated].to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_Estimated_District_Records.csv",
    index=False
)

# 6. Save records carrying a Verified label for manual review.
# The filename explicitly indicates these labels are not proof.
df.loc[is_labelled_verified].to_csv(
    BASE_DIR / "RoadSense_AI_Task_4_Verified_Label_Review.csv",
    index=False
)

print("Task 4 analytics completed.")
print(f"Total dataset rows: {len(df)}")
print(f"State/UT-labelled records: {int(is_state_total.sum())}")
print(f"Estimated records: {int(is_estimated.sum())}")
print(f"Records carrying a Verified label: {int(is_labelled_verified.sum())}")
print()
print("Created:")
print("- Data quality summary")
print("- Data status counts")
print("- District record counts by State/UT")
print("- Source verification review")
print("- Estimated district records")
print("- Verified-label review")
print()
print("No original dataset values were changed.")
print("Records still require source verification.")