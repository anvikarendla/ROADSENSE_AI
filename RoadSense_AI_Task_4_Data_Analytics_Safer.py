"""RoadSense.ai Task 4: safer descriptive analytics and source-review files.
Place this script beside RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv.
It does not independently verify source values and deliberately creates no district ranking.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'RoadSense_AI_Task_3_Cleaned_Road_Accident_Data_2022.csv'
if not INPUT.exists():
    raise FileNotFoundError(f'Missing {INPUT.name}. Put this script beside the Task 3 cleaned CSV.')
df = pd.read_csv(INPUT)
required = ['Year','State/UT','District','Accident Cases','Injured','Died','Data Status','Source']
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f'Missing columns: {missing}')
for c in ['State/UT','District','Data Status','Source']:
    df[c] = df[c].fillna('').astype(str).str.strip()
for c in ['Year','Accident Cases','Injured','Died']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
status = df['Data Status'].str.casefold()
source = df['Source'].str.casefold()
state = df['State/UT'].str.casefold()
is_state = status.str.contains('official state/ut data', regex=False)
is_est = status.str.contains('estimated', regex=False)
is_verified_label = status.str.contains('verified', regex=False)
is_tn = state.eq('tamil nadu')
is_haryana = state.eq('haryana')
tn_source = source.str.contains('tamil nadu transport department', regex=False)
haryana_source = source.str.contains('statistical abstract of haryana', regex=False)
metrics = ['Accident Cases','Injured','Died']
repeat_count = df.groupby(['State/UT'] + metrics, dropna=False)['District'].transform('size')
repeated = repeat_count.gt(1)

summary = [
 ('Dataset rows',len(df)),('Distinct State/UT labels',df['State/UT'].replace('',pd.NA).nunique()),
 ('Distinct district labels',df['District'].replace('',pd.NA).nunique()),
 ('Missing Year',int(df['Year'].isna().sum())),('Missing State/UT',int(df['State/UT'].eq('').sum())),
 ('Missing District',int(df['District'].eq('').sum())),('Missing Accident Cases',int(df['Accident Cases'].isna().sum())),
 ('Missing Injured values',int(df['Injured'].isna().sum())),('Missing deaths',int(df['Died'].isna().sum())),
 ('Exact duplicate rows',int(df.duplicated().sum())),('Records labelled Official State/UT data',int(is_state.sum())),
 ('Records labelled Estimated',int(is_est.sum())),('Records carrying a Verified label (not independent proof)',int(is_verified_label.sum())),
 ('Records with repeated metrics within a state (review signal)',int(repeated.sum())),
 ('Tamil Nadu records',int(is_tn.sum())),('Tamil Nadu records naming Transport Department',int((is_tn & tn_source).sum())),
 ('Haryana records',int(is_haryana.sum())),('Haryana records naming Statistical Abstract',int((is_haryana & haryana_source).sum()))]
pd.DataFrame(summary,columns=['Metric','Value']).to_csv(BASE/'RoadSense_AI_Task_4_Data_Quality_Summary.csv',index=False)
df['Data Status'].replace('', 'Missing status').value_counts().rename_axis('Data Status').reset_index(name='Record Count').to_csv(BASE/'RoadSense_AI_Task_4_Data_Status_Counts.csv',index=False)
df.groupby('State/UT',dropna=False).size().reset_index(name='Dataset Records').sort_values('Dataset Records',ascending=False).to_csv(BASE/'RoadSense_AI_Task_4_District_Record_Counts_by_State.csv',index=False)
review = df.copy()
review['Review Outcome'] = 'Needs source and geographic-level verification'
review.loc[is_est,'Review Outcome'] = 'Estimated - do not present as verified district data'
review.loc[is_state,'Review Outcome'] = 'State/UT-labelled record - confirm geographic level before district analysis'
review.loc[is_tn & tn_source,'Review Outcome'] = 'Tamil Nadu source named - check each metric against official report'
review.loc[is_haryana & haryana_source,'Review Outcome'] = 'Haryana source named - check each metric against Table 22.3'
review['Repeated Metrics Review'] = ''
review.loc[repeated,'Repeated Metrics Review'] = 'Same metrics occur for multiple districts in this state; inspect source'
review.to_csv(BASE/'RoadSense_AI_Task_4_Source_Verification_Review.csv',index=False)
df.loc[is_est].to_csv(BASE/'RoadSense_AI_Task_4_Estimated_District_Records.csv',index=False)
df.loc[is_verified_label].to_csv(BASE/'RoadSense_AI_Task_4_Verified_Label_Review.csv',index=False)
candidate = (~is_state & ~is_est & df['State/UT'].ne('') & df['District'].ne('') & df[metrics].notna().all(axis=1))
check = df.loc[candidate].copy()
check['Verification Warning'] = 'Candidate only: status label is not independent proof; verify each metric against a reliable district-level source before ranking.'
check.to_csv(BASE/'RoadSense_AI_Task_4_District_Records_For_Source_Check.csv',index=False)
print('Task 4 analytics completed successfully.')
print(f'Dataset rows: {len(df)}')
print(f'State/UT-labelled records excluded from district rankings: {int(is_state.sum())}')
print(f'Estimated records excluded from district rankings: {int(is_est.sum())}')
print(f'Records carrying a Verified label (still need source checks): {int(is_verified_label.sum())}')
print(f'Records queued for source checking: {len(check)}')
print('Created/updated summary, status counts, state record counts, source review, estimated records, verified-label review, and source-check queue.')
print('No top-district ranking generated because independent source verification is incomplete.')
print('Original Task 3 cleaned CSV was not modified.')
