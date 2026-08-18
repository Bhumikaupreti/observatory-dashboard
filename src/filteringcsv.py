import pandas as pd

df = pd.read_csv("../data/raw/observatory_10min_hypothetical_data.csv")

print("First 5 rows:")
print(df.head())

print("\nNumber of rows and columns:")
print(df.shape)

print("\nColumn names:")
print(df.columns)

df["Timestamp"] = pd.to_datetime(
    df["Date"] + " " + df["Time"]
)

print("\nTimestamp:")
print(df[["Date", "Time", "Timestamp"]].head(10))
print(df.dtypes)
missing_values = df.isnull().sum()

print("Missing values:")
print(missing_values)
missing_rows = df[df.isnull().any(axis=1)]

print(missing_rows)
missing_percentage = (df.isnull().sum() / len(df)) * 100
print(missing_percentage)
duplicate_rows = df.duplicated().sum()

print("Duplicate rows:", duplicate_rows)
duplicates = df[df.duplicated(keep=False)]

print("Duplicate rows:")
print(duplicates)
duplicate_timestamps = df["Timestamp"].duplicated().sum()

print("Duplicate timestamps:", duplicate_timestamps)
df["Duplicate_Flag"] = df.duplicated(keep=False)
print(df[df["Duplicate_Flag"]])
invalid_rh = df[
    (df["RH_percent"] < 0) |
    (df["RH_percent"] > 100)
]
print("Invalid RH values:")
print(invalid_rh[["Timestamp", "RH_percent"]])
print("Number of invalid RH values:", len(invalid_rh))

invalid_wind = df[
    df["Wind_Speed_mps"] < 0
]

print("Invalid Wind Speed values:")
print(invalid_wind[["Timestamp" , "Wind_Speed_mps"]])
print("Number of invalid Wind Speed values:", len(invalid_wind))
invalid_direction = df[
    (df["Wind_Direction_deg"] < 0) |
    (df["Wind_Direction_deg"] > 360)
]
print("Invalid Wind Direction values:")
print(invalid_direction[["Timestamp", "Wind_Direction_deg"]])

print("Number of invalid Wind Direction values:", len(invalid_direction))
df["Time_only"] = df["Timestamp"].dt.time
sunrise = pd.Timestamp("04:30").time()
sunset = pd.Timestamp("18:30").time()
solar_invalid = (
    (
        (df["Time_only"] < sunrise) |
        (df["Time_only"] > sunset)
    )
    &
    (df["SR_Wm2"] > 0)
)
solar_invalid_count = solar_invalid.sum()

print("Invalid Solar Radiation Records:", solar_invalid_count)
# -----------------------------
# 3-SIGMA OUTLIER CHECK
# -----------------------------

parameters = [
    "Pressure_hPa",
    "Temperature_C",
    "RH_percent",
    "Wind_Speed_mps",
    "Wind_Direction_deg",
    "SR_Wm2"
]

outlier_results = {}

for parameter in parameters:

    # Calculate mean and standard deviation
    mean = df[parameter].mean()
    std = df[parameter].std()

    # Calc
    lower_limit = mean - (3 * std)
    upper_limit = mean + (3 * std)

    outliers = (
        (df[parameter] < lower_limit) |
        (df[parameter] > upper_limit)
    )

    outlier_results[parameter] = {
        "Mean": mean,
        "Std_Deviation": std,
        "Lower_Limit": lower_limit,
        "Upper_Limit": upper_limit,
        "Outlier_Count": outliers.sum()
    }

outlier_summary = pd.DataFrame(outlier_results).T

print(outlier_summary)
