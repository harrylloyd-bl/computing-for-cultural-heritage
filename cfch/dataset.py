from config import RAW_DATA_DIR

import pandas as pd


def process_raw_xlsx():
    """
    Use Alex Hailey's s/s "ior_l_mar_shipsMC.xlsx" and the main Metadata s/s "IAMS_pre_cyber_export_Corporation_authority.xlsx"
    Retain the index from AH's s/s, and take the properly encoded 'History' column from the other s/s
    Strip a load of xml formatting to clean up the History column, add it to the AH s/s and export
    :return: pd.DataFrame
    """
    alex_hailey_ss_path = RAW_DATA_DIR / "ior_l_mar_shipsMC.xlsx"
    iams_ss_path = RAW_DATA_DIR / "IAMS_pre_cyber_export_Corporation_authority.xlsx"

    ah_df = pd.read_excel(alex_hailey_ss_path, index_col="RecordID", na_values=-9999.0, sheet_name="Orig")
    iams_df = pd.read_excel(iams_ss_path, sheet_name="IAMS_Corporation", index_col="IAMSRecordId", na_values=" ")

    clean_history = iams_df.loc[ah_df.index, "History_XML"].str.strip(
        "<History>").str.strip(
        "</History>").str.replace(
        "P>", "").str.rstrip(
        "</P").str.replace(
        "</P><P>", " ").str.replace(
        "</<", " ").str.replace(
        '<emph render="italic">', "").str.replace(
        "</emph>", "").str.replace(
        "&amp;", "&").rename("History")

    ah_df["History"] = clean_history
    ships_df = ah_df[["CorporateName", "History", "DateRange"]]
    return ships_df


def process_csv_to_sample(ships_df):
    """
    These ship IDs were selected from the clean_ships list and checked to ensure that they parsed well using the basic teacing parser
    They were chosen from the first 20 of the clean_ships with a DateRange that wasn't 'Unspecified'
    `ships_df.loc[pd.Index(clean_ships)].query("DateRange != 'Unspecified'").iloc[:20]`
    See data/raw/sample_annotations.txt for the raw analysis to choose these.
    The following were removed:
    045-001114929
    """
    ground_truth_index = pd.Index(
        [
            '045-001114649', '045-001114662', '045-001114683', '045-001114707',
            '045-001114757', '045-001114838', '045-001114858', '045-001114912',
            '045-001114937', '045-001114938', '045-001114954', '045-001114961',
            '045-001114966', '045-001115008', '045-001115013', '045-001115014',
            '045-001115015', '045-001115054', '045-001115063'
        ]
    )

    sample_df = ships_df.loc[ground_truth_index].rename(columns={"CorporateName": "ShipName"}).rename_axis(index="RecordID")
    return sample_df


def main():
    ships_output_path = RAW_DATA_DIR / "ships.csv"
    sample_output_path = RAW_DATA_DIR / "clean_ships_sample.csv"

    ships_df = process_raw_xlsx()
    ships_df.to_csv(ships_output_path, encoding="utf8")
    print("Ships df exported")

    sample_df = process_csv_to_sample(ships_df)
    sample_df.to_csv(sample_output_path, encoding="utf8")
    print("Sample df exported")


if __name__ == "__main__":
    main()
    print("Raw data processing complete")
