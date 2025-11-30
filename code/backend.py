import numpy as np
import pandas as pd
import geopandas as gpd
import altair as alt
from sklearn.preprocessing import MinMaxScaler # for normalization
from umap import UMAP # for dimenensionality reduction

print("Creating dataframe...")
# import dataframe
df = pd.read_csv("COVID-19_Cases,_Tests,_and_Deaths_by_ZIP_Code_-_Historical_20251017.csv")

print("dataframe read successfully")

###################################### TASK 1 #############################################
# ----------------------------- 1.1 Construct embeddings ----------------------------------

# Concatenate normalized numeric attribute


print(f"Original Data : \n{df}")
print("*" * 120) 

# Clean columns for normalization

# remove commas from numeric values
df['Cases - Cumulative'] = df['Cases - Cumulative'].str.replace(',', '').astype(float)
df['Population'] = df['Population'].str.replace(',', '').astype(float)
df['Tests - Weekly'] = df['Tests - Weekly'].str.replace(',', '').astype(float)
df['Case Rate - Cumulative'] = df['Case Rate - Cumulative'].str.replace(',', '').astype(float)
df['Cases - Weekly'] = df['Cases - Weekly'].str.replace(',', '').astype(float)
df['Tests - Cumulative'] = df['Tests - Cumulative'].str.replace(',', '').astype(float)
df['Test Rate - Cumulative'] = df['Test Rate - Cumulative'].str.replace(',', '').astype(float)

# remove percentage sign
df['Percent Tested Positive - Weekly'] = df['Percent Tested Positive - Weekly'].str.replace('%', '').astype(float)
df['Percent Tested Positive - Cumulative'] = df['Percent Tested Positive - Cumulative'].str.replace('%', '').astype(float)



# parse geographic coordinates
df[['Longitude', 'Latitude']] = df['ZIP Code Location'].str.extract(r'POINT \((?P<Longitude>[^ ]+)\s+(?P<Latitude>[^)]+)\)')

df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')

# change to datetime
df['Week Start'] = pd.to_datetime(df['Week Start'])
df['Week End'] = pd.to_datetime(df['Week End'])

# drop the null values in longitude latitude
df = df.dropna(subset=['Longitude', 'Latitude'])

# change NaN to 0
df = df.fillna(0)

print(f"Cleaned Data: \n{df}")
print("*" * 120) 

# Implement Normalization Logic

numeric_cols = ['Cases - Cumulative', 'Population', 'Tests - Weekly', 
                'Case Rate - Cumulative', 'Cases - Weekly', 
                'Tests - Cumulative', 'Test Rate - Cumulative', 
                'Percent Tested Positive - Weekly', 
                'Percent Tested Positive - Cumulative',
                'Longitude', 'Latitude'
                ]

# This creates a unique ID for each record
df['Record_ID'] = df.index

scaler = MinMaxScaler()

# Create a new DataFrame for the normalized values
df_normalized = pd.DataFrame(scaler.fit_transform(df[numeric_cols]), columns=numeric_cols)

# Rename columns for the final embedding file
df_normalized.columns = [f'feat_{i+1}' for i in range(len(numeric_cols))]

# Combine unique ID with the normalized features

df_embeddings = pd.concat([df['Record_ID'], df_normalized], axis=1)

print(f"Embeddings Data: \n{df_embeddings}")
print("*" * 120)


# Define number of groups for population density aggregation

num_quantiles = 4

# we can use pd.qcut to create quantile - based bins
df['Population_Stratum'] = pd.qcut(
    df['Population'],
    q=num_quantiles,
    labels=['Q1_Low', 'Q2_Medium', 'Q3_High', 'Q4_Very_High'],
    duplicates='drop',
    precision = 0
)

# Convert new feature to string type for stability in grouping
df['Population_Stratum'] = df['Population_Stratum'].astype(str)

print("Population Stratums created successfully.")
print(f"Data with Population Stratums \n{df[['Population', 'Population_Stratum']].head(10)}")

# Groupy by week and the new Stratum, then calculate the mean of the metric

stratified_weekly_mean = df.groupby(
    ['Week End', 'Population_Stratum']
)['Case Rate - Cumulative'].mean().reset_index()

# Rename aggregated column
stratified_weekly_mean.rename(
    columns={'Case Rate - Cumulative': 'Stratum_Mean_Case_Rate'},
    inplace=True
)

# Merge aggregated data back into the original DF

df = df.merge(
    stratified_weekly_mean,
    on = ['Week End', 'Population_Stratum'],
    how='left'
)

print("\nAggregated Feature (Stratum Mean Case Rate) created successfully.")
print(df[['Week End', 'Population_Stratum', 'Case Rate - Cumulative', 'Stratum_Mean_Case_Rate']].head())

# now we can scale the new feature and add to embeddings

stratum_scaler_agg = MinMaxScaler()
agg_feature_scaled = stratum_scaler_agg.fit_transform(df[['Stratum_Mean_Case_Rate']])

# create temp df
df_agg_feat = pd.DataFrame(
    agg_feature_scaled,
    columns = ['feat_12']
)


# clean before saving
df_agg_feat.fillna(0)

# add scaled feature to og DF

new_feat_name = f'feat_{len(df_embeddings.columns)}'

# add new feature to embeddings DF

df_embeddings[new_feat_name] = df_agg_feat['feat_12']



# Save embeddings to CSV file
print("Saving embeddings to embeddings.csv...")
df_embeddings.to_csv('embeddings.csv', index = False)
print("Embeddings saved successfully to 'embeddings.csv'.")


# Task 1.2 Dimensionality Reduction using UMAP


# Load featured data

df_embeddings = pd.read_csv('embeddings.csv')
feature_cols  = [col for col in df_embeddings.columns if col.startswith('feat_')]
X = df_embeddings[feature_cols]

# initialilze UMAP reducer
umap_reducer = UMAP(
    n_neighbors = 15,
    n_components = 2,
    min_dist = 0.1,
    random_state = 42
)

# cleaning for NaN values
X = X.fillna(0)

# fit and transform the data
print("Transforming embeddings using UMAP...")
print(f"Original Embedding Shape: {X.shape}")
print(f"Number of NA: {X.isna().sum()}")

X_projected = umap_reducer.fit_transform(X)
print("UMAP transformation completed.")

df_projection = pd.DataFrame(
    X_projected,
    columns = ['UMAP_1', 'UMAP_2']
)

df_projection['Record_ID'] = df_embeddings['Record_ID']
# we are going to merge more items than just stratum

cols = [
    'Record_ID',
    'Population_Stratum',
    'Week End',
    'ZIP Code',
    'Latitude',
    'Longitude',
    'Case Rate - Cumulative'
]

df_projection = df_projection.merge(
    df[cols],
    on='Record_ID',
    how='left'
)

# we have one final clean to do to remove ghost points with NaN values
df_projection = df_projection.dropna(subset=['Record_ID'])
print(f"Final projection dataframe cleaned of NaN Record_IDs. : {len(df_projection)} records remaining.")

# save projection to csv
df_projection.to_csv('embeddings_umap.csv', index = False)
print("UMAP projection saved successfully to 'embeddings_umap.csv'.")

print(f"Projected Dimensionality Reduced Data: \n{df_projection}")

# Load up visualization libraries
import altair as alt

alt.data_transformers.enable('default', max_rows = 4999)

df_viz = df_projection.sample(n = 4900, random_state = 42)

# create UMAP scatter plot
umap_chart = alt.Chart(df_viz).mark_point(size = 60).encode(
    x = alt.X('UMAP_1', title = 'UMAP Dimension 1'),
    y = alt.Y('UMAP_2', title = 'UMAP Dimension 2'),
    color = alt.Color('Population_Stratum', title = 'Population Density'),
    tooltip = ['Record_ID', 'Population_Stratum', 'UMAP_1', 'UMAP_2']
).properties(
    title = 'UMAP Projection of COVID-19 Data Embeddings'
).interactive()

vega_lite_spec = umap_chart.to_json(indent = 2)

print('\n---- Vega-Lite JSON Specification Output ----')
print(vega_lite_spec)

{
"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
"description": "UMAP Projection of COVID-19 Data Embeddings",
"data": {
    "url" : "embeddings_umap.csv"
},
"mark":{ 
  "type": "point",
  "tooltip": True
},
"encoding": {
  "x": {
    "field": "UMAP_1",
    "type": "quantitative",
    "title": "UMAP Dimension 1"
    },
    "y": {
      "field": "UMAP_2",
      "type":  "quantitative",
      "title": "UMAPDimension 2"
    },
    "color": {
      "field": "Population_Stratum",
      "type": "nominal",
      "title": "Population Density"
    }
  },
  "width": 600,
  "height": 400
}