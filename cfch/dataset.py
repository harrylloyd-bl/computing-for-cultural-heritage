from pathlib import Path

import pandas as pd

from config import RAW_DATA_DIR


def main():
    input_path = RAW_DATA_DIR / "ships.csv"
    output_path = RAW_DATA_DIR / "ship_name_history.csv"
       
    ships_df = pd.read_csv(input_path, index_col="RecordID", na_values=-9999.0)
    ships_df[["CorporateName", "History", "DateRange"]].to_csv(output_path)


if __name__ == "__main__":
    main()
