"""RoadSense.ai Task 5: Data Visualization (improved version)

Input: RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv
Outputs: four PNG charts and a chart-record review CSV.

Important: Existing Data Status labels and Source strings are not, by themselves,
independent verification. Rankings below use the 27 Tamil Nadu rows whose source
field names the Tamil Nadu Transport Department. The cited Tamil Nadu comparison
table supports accident and death counts; injury values need separate verification.
These are not India-wide rankings.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv"
OUT_DIR = BASE_DIR

df = pd.read_csv(DATA_FILE)
for col in ["Accident Cases", "Injured", "Died"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

status = df["Data Status"].fillna("Missing status").astype(str).str.strip()
source = df["Source"].fillna("").astype(str).str.strip()
state = df["State/UT"].fillna("").astype(str).str.strip()

# Candidate district records with the expected Tamil Nadu source label.
# This filter selects records for review; it does not independently validate them.
tn_candidates = df.loc[
    state.str.casefold().eq("tamil nadu")
    & source.str.contains("Tamil Nadu Transport Department", case=False, regex=False)
].copy()

# Remove missing metric rows from charts that compare all three numeric metrics.
chart_df = tn_candidates.dropna(
    subset=["District", "Accident Cases", "Injured", "Died"]
).copy()
chart_df["District Label"] = chart_df["District"].astype(str) + " (Tamil Nadu)"
chart_df.to_csv(OUT_DIR / "RoadSense_AI_Task_5_Chart_Records_For_Review.csv", index=False)

# Chart 1: accident cases, horizontal bars with values.
top_acc = chart_df.nlargest(10, "Accident Cases").sort_values("Accident Cases")
fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(top_acc["District Label"], top_acc["Accident Cases"])
ax.bar_label(bars, fmt="{:,.0f}", padding=4)
ax.set_xlabel("Reported accident cases")
ax.set_ylabel("District")
ax.set_title("Top 10 Tamil Nadu district records by accident cases (2022)")
ax.text(0, -0.16, "Selected source-labelled records; metric-level source review required. Not an India-wide ranking.", transform=ax.transAxes, fontsize=9, va="top")
ax.set_xlim(0, max(top_acc["Accident Cases"]) * 1.15)
fig.tight_layout()
fig.savefig(OUT_DIR / "Task5_Top_Districts_Accidents.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Chart 2: relationship between accident cases and injuries.
fig, ax = plt.subplots(figsize=(8.5, 6.5))
ax.scatter(chart_df["Accident Cases"], chart_df["Injured"], alpha=0.8)
ax.set_xlabel("Reported accident cases")
ax.set_ylabel("Injured people (dataset value; verification pending)")
ax.set_title("Accident cases vs injuries — selected Tamil Nadu records")
ax.text(0, -0.17, "The pattern is descriptive only; injury counts need separate source verification. Association does not prove causation.", transform=ax.transAxes, fontsize=9, va="top", wrap=True)
fig.tight_layout()
fig.savefig(OUT_DIR / "Task5_Cases_vs_Injuries.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Chart 3: deaths, horizontal bars with values.
top_deaths = chart_df.nlargest(10, "Died").sort_values("Died")
fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(top_deaths["District Label"], top_deaths["Died"])
ax.bar_label(bars, fmt="{:,.0f}", padding=4)
ax.set_xlabel("Reported deaths")
ax.set_ylabel("District")
ax.set_title("Top 10 Tamil Nadu district records by deaths (2022)")
ax.text(0, -0.16, "Selected source-labelled records; metric-level source review required. Not an India-wide ranking.", transform=ax.transAxes, fontsize=9, va="top")
ax.set_xlim(0, max(top_deaths["Died"]) * 1.15)
fig.tight_layout()
fig.savefig(OUT_DIR / "Task5_Top_Districts_Deaths.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Chart 4: status categories as a readable horizontal bar chart.
status_counts = status.value_counts().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(status_counts.index.astype(str), status_counts.values)
ax.bar_label(bars, fmt="{:,.0f}", padding=4)
ax.set_xlabel("Number of records")
ax.set_ylabel("Existing Data Status label")
ax.set_title("RoadSense.ai dataset records by existing data-status label")
ax.text(0, -0.16, "Labels reflect the working CSV and are not independent proof of source accuracy.", transform=ax.transAxes, fontsize=9, va="top")
ax.set_xlim(0, max(status_counts.values) * 1.15)
fig.tight_layout()
fig.savefig(OUT_DIR / "Task5_Data_Status.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Improved Task 5 charts generated successfully.")
print(f"Dataset rows: {len(df)}")
print(f"Tamil Nadu rows selected by source description: {len(tn_candidates)}")
print(f"Rows used in the four metric charts: {len(chart_df)}")
print("Injury figures remain subject to independent source verification.")


# Chart 5: Pie chart showing data-status distribution.
fig, ax = plt.subplots(figsize=(11, 7))

wedges, texts, autotexts = ax.pie(
    status_counts.values,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.75,
    wedgeprops={"edgecolor": "white"}
)

ax.legend(
    wedges,
    status_counts.index.astype(str),
    title="Data Status",
    loc="center left",
    bbox_to_anchor=(1, 0.5)
)

ax.set_title("RoadSense.ai Dataset Distribution by Data Status")
ax.axis("equal")

fig.tight_layout()
fig.savefig(OUT_DIR / "Task5_Data_Status_Pie_Chart.png", dpi=180, bbox_inches="tight")
plt.close(fig)