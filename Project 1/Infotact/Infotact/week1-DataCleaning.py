import os
import pandas as pd

def main():
    # ----------------------------------
    # STEP 1: Read clean CSV
    # ----------------------------------
    csv_path = r"C:\Users\PRAKRATHI\OneDrive\Desktop\Infotact\sensor_data.csv"
    df = pd.read_csv(csv_path)

    # ----------------------------------
    # STEP 2: Rename columns
    # ----------------------------------
    df = df.rename(columns={
        "Air temperature [K]": "air_temp",
        "Process temperature [K]": "process_temp",
        "Rotational speed [rpm]": "rotation_speed",
        "Torque [Nm]": "torque",
        "Tool wear [min]": "tool_wear",
        "Machine failure": "failure"
    })

    # ----------------------------------
    # STEP 3: Add machine_id & timestamp
    # ----------------------------------
    df["machine_id"] = "M01"
    df["timestamp"] = pd.date_range(
        start="2025-01-01",
        periods=len(df),
        freq="h"   # FIXED warning
    )

    # ----------------------------------
    # STEP 4: Sort
    # ----------------------------------
    df = df.sort_values(by=["machine_id", "timestamp"])

    # ----------------------------------
    # STEP 5: Sensor columns
    # ----------------------------------
    sensor_cols = [
        "air_temp",
        "process_temp",
        "rotation_speed",
        "torque",
        "tool_wear"
    ]

    # ----------------------------------
    # STEP 6: SAFE interpolation (COLUMN-WISE)
    # ----------------------------------
    for col in sensor_cols:
        df[col] = df.groupby("machine_id")[col].transform(
            lambda x: x.interpolate()
        )

    # ----------------------------------
    # STEP 7: Lag features
    # ----------------------------------
    for lag in [1, 2]:
        for col in sensor_cols:
            df[f"{col}_lag_{lag}"] = (
                df.groupby("machine_id")[col].shift(lag)
            )

    # ----------------------------------
    # STEP 8: Rolling features
    # ----------------------------------
    df["air_temp_roll_mean_3"] = (
        df.groupby("machine_id")["air_temp"]
        .transform(lambda x: x.rolling(3).mean())
    )

    df["rotation_speed_roll_std_3"] = (
        df.groupby("machine_id")["rotation_speed"]
        .transform(lambda x: x.rolling(3).std())
    )

    # ----------------------------------
    # STEP 9: Drop NaNs
    # ----------------------------------
    df = df.dropna()

    # ----------------------------------
    # ----------------------------------
    # STEP 10: Save output in SAME folder
    # ----------------------------------
    base_dir = os.path.dirname(csv_path)  # original file folder
    output_path = os.path.join(base_dir, "week1_cleaned_data.csv")

    df.to_csv(output_path, index=False)

    print("✅ Week 1 data engineering completed successfully")


if __name__ == "__main__":
    main()