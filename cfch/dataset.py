from config import RAW_DATA_DIR

import pandas as pd


def main():
    alex_hailey_ss_path = RAW_DATA_DIR / "ior_l_mar_shipsMC.xlsx"
    iams_ss_path = RAW_DATA_DIR / "IAMS_pre_cyber_export_Corporation_authority.xlsx"
    output_path = RAW_DATA_DIR / "ships.csv"
       
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
    ah_df[["CorporateName", "History", "DateRange"]].to_csv(output_path, encoding="utf8")


if __name__ == "__main__":
    main()
    print("Raw data processing complete")
