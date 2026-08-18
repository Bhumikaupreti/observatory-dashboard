import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Observatory Dashboard",
    page_icon="🔭"
)

st.title("🔭 Observatory Data Dashboard")

st.write("Upload your observational data")


# ==========================================
# 1. FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
)


if uploaded_file is not None:

    # ==========================================
    # 2. READ FILE
    # ==========================================

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)


    st.success("✅ File uploaded successfully!")


    # ==========================================
    # 3. DATA INFORMATION
    # ==========================================

    st.write("### Dataset Information")

    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])


    # ==========================================
    # 4. REQUIRED COLUMNS
    # ==========================================

    required_columns = [
        "Date",
        "Time",
        "Pressure_hPa",
        "Temperature_C",
        "RH_percent",
        "Wind_Speed_mps",
        "Wind_Direction_deg",
        "SR_Wm2"
    ]


    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]


    # ==========================================
    # 5. COLUMN VALIDATION
    # ==========================================

    if missing_columns:

        st.error("❌ Required columns are missing:")

        for column in missing_columns:
            st.write("-", column)


    else:

        st.success("✅ All required columns are present!")


        # ==========================================
        # 6. SHOW DATA
        # ==========================================

        st.write("### Uploaded Data")

        st.dataframe(df)


        # ==========================================
        # 7. CREATE TIMESTAMP
        # ==========================================

        df["Timestamp"] = pd.to_datetime(
            df["Date"].astype(str)
            + " "
            + df["Time"].astype(str),
            errors="coerce"
        )


        st.write("### Timestamp")

        st.dataframe(
            df[
                ["Date", "Time", "Timestamp"]
            ].head(10)
        )


        # ==========================================
        # 8. TIME INTERVAL CHECK
        # ==========================================

        df["Time_Difference"] = df["Timestamp"].diff()

        expected_interval = pd.Timedelta(
            minutes=10
        )

        irregular_intervals = (
            df["Time_Difference"].notna()
            &
            (
                df["Time_Difference"]
                != expected_interval
            )
        )


        st.write("### Time Interval Check")

        st.write(
            "Expected interval: 10 minutes"
        )

        st.write(
            "Irregular intervals:",
            int(irregular_intervals.sum())
        )


        # ==========================================
        # 9. MISSING VALUE CHECK
        # ==========================================

        missing_values = df.isnull().sum()

        total_missing = int(
            missing_values.sum()
        )


        st.write("### Missing Value Check")

        st.write(
            "Total missing values:",
            total_missing
        )


        if total_missing > 0:

            st.warning(
                "⚠️ Missing values detected"
            )

            st.dataframe(
                missing_values[
                    missing_values > 0
                ]
            )

        else:

            st.success(
                "✅ No missing values"
            )


        # ==========================================
        # 10. DUPLICATE CHECK
        # ==========================================

        duplicate_rows = df.duplicated().sum()


        st.write("### Duplicate Check")

        st.write(
            "Duplicate rows:",
            int(duplicate_rows)
        )


        if duplicate_rows > 0:

            st.warning(
                f"⚠️ {duplicate_rows} "
                "duplicate row(s) detected"
            )

        else:

            st.success(
                "✅ No duplicate rows"
            )


        # ==========================================
        # 11. PHYSICAL VALIDITY CHECK
        # ==========================================

        st.write("### Physical Validity Check")


        invalid_rh = (
            (df["RH_percent"] < 0)
            |
            (df["RH_percent"] > 100)
        )


        invalid_wind_speed = (
            df["Wind_Speed_mps"] < 0
        )


        invalid_wind_direction = (
            (df["Wind_Direction_deg"] < 0)
            |
            (df["Wind_Direction_deg"] >= 360)
        )


        invalid_sr = (
            df["SR_Wm2"] < 0
        )


        st.write(
            "Invalid RH values:",
            int(invalid_rh.sum())
        )

        st.write(
            "Negative wind speed:",
            int(invalid_wind_speed.sum())
        )

        st.write(
            "Invalid wind direction:",
            int(invalid_wind_direction.sum())
        )

        st.write(
            "Negative solar radiation:",
            int(invalid_sr.sum())
        )


        # ==========================================
        # 12. 3-SIGMA CHECK
        # ==========================================

        st.write("### 3-Sigma Outlier Check")


        parameters = [
            "Pressure_hPa",
            "Temperature_C",
            "RH_percent",
            "Wind_Speed_mps",
            "SR_Wm2"
        ]


        sigma_results = {}


        for parameter in parameters:

            mean = df[parameter].mean()

            std = df[parameter].std()

            lower_limit = mean - 3 * std

            upper_limit = mean + 3 * std


            outliers = (
                (df[parameter] < lower_limit)
                |
                (df[parameter] > upper_limit)
            )


            sigma_results[parameter] = int(
                outliers.sum()
            )


        for parameter, count in sigma_results.items():

            st.write(
                parameter,
                "3-sigma outliers:",
                count
            )


        # ==========================================
        # 13. QUALITY FLAG
        # ==========================================

        st.write("### Quality Control Flags")


        df["Quality_Flag"] = "GOOD"


        # Missing
        missing_row = (
            df[required_columns]
            .isnull()
            .any(axis=1)
        )


        df.loc[
            missing_row,
            "Quality_Flag"
        ] = "MISSING"


        # Duplicate
        duplicate_row = df.duplicated()


        df.loc[
            duplicate_row,
            "Quality_Flag"
        ] = "DUPLICATE"


        # Invalid physical values
        invalid_row = (
            invalid_rh
            |
            invalid_wind_speed
            |
            invalid_wind_direction
            |
            invalid_sr
        )


        df.loc[
            invalid_row,
            "Quality_Flag"
        ] = "INVALID"


        # Time error
        df.loc[
            irregular_intervals,
            "Quality_Flag"
        ] = "TIME_ERROR"


        # ==========================================
        # 14. QUALITY SUMMARY
        # ==========================================

        st.write("### Quality Summary")

        st.dataframe(
            df["Quality_Flag"]
            .value_counts()
        )


        # ==========================================
        # 15. QUALITY-CONTROLLED DATA
        # ==========================================

        st.write(
            "### Quality-Controlled Data"
        )


        st.dataframe(
            df[
                [
                    "Timestamp",
                    "Temperature_C",
                    "RH_percent",
                    "Wind_Speed_mps",
                    "Wind_Direction_deg",
                    "SR_Wm2",
                    "Quality_Flag"
                ]
            ]
        )
                # ==========================================
        # 16. PARAMETER SELECTION
        # ==========================================

        st.write("### Select Parameter")

        parameter = st.selectbox(
            "Choose a parameter",
            [
                "Pressure_hPa",
                "Temperature_C",
                "RH_percent",
                "Wind_Speed_mps",
                "Wind_Direction_deg",
                "SR_Wm2"
            ]
        )
                # ==========================================
        # 17. RAW TIME SERIES PLOT
        # ==========================================

        st.write("### Raw Observation Plot")

        chart_data = df[
            ["Timestamp", parameter]
        ].dropna()

        st.line_chart(
            chart_data.set_index("Timestamp")
        )