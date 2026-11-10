"""RoadSense_AI Task 3: Data Cleaning. Run in the same folder as the input CSV."""
import pandas as pd
INPUT_FILE = "RoadSense_AI_Task_2_Road_Accident_Data_2022.csv"
OUTPUT_FILE = "RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv"
df = pd.read_csv(INPUT_FILE)
for col in ["State/UT", "District", "Data Status", "Source"]:
    df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
for col in ["Record ID", "Year", "Accident Cases", "Injured", "Died"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
before = len(df)
df = df.drop_duplicates().copy()
print(f"Exact duplicate rows removed: {before - len(df)}")
metrics = ["Accident Cases", "Injured", "Died"]
repeat = df.groupby(["State/UT"] + metrics, dropna=False)["District"].transform("count").gt(1)
df["Data Quality Note"] = ""
df.loc[repeat, "Data Quality Note"] = "Same accident metrics appear for multiple districts in this state; verify against district-level source"
missing = df[["Year", "State/UT", "District"]].isna().any(axis=1)
df.loc[missing, "Data Quality Note"] = df.loc[missing, "Data Quality Note"].astype(str).apply(lambda x: (x + "; " if x else "") + "Missing required field")
df.to_csv(OUTPUT_FILE, index=False)
print(f"Cleaned dataset saved to: {OUTPUT_FILE}")
print(f"Rows: {len(df)}; columns: {len(df.columns)}")
print("Review Data Quality Note and source status before treating district values as verified.")
