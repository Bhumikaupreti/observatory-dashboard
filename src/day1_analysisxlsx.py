import pandas as pd

df = pd.read_excel("../data/raw/observatory_10min_hypothetical_data.xlsx")

print("First 5 rows:")
print(df.head())

print("\nNumber of rows and columns:")
print(df.shape)

print("\nColumn names:")
print(df.columns)

# Create Timestamp
df["Timestamp"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Time"].astype(str)
)

print("\nTimestamp:")
print(df[["Date", "Time", "Timestamp"]].head(10))

# Check time interval
df["Time_Difference"] = df["Timestamp"].diff()

print("\nTime differences:")
print(df["Time_Difference"].value_counts())