from cfch.config import RAW_DATA_DIR

import pandas as pd


def import_data(f: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Import the ships dataframe to four lists instead of a df
    Use lists as a less complex data structure than df, dfs aren't focus of training pt 1.
    """
    ship_df = pd.read_csv(f, index_col=0, encoding="utf8")
    ship_ids = ship_df.index.tolist()
    names = ship_df["ShipName"].tolist()
    histories = ship_df["History"].tolist()
    date_ranges = ship_df["DateRange"].tolist()
    return ship_ids, names, histories, date_ranges


def teaching_parse(ship_ids, names, date_ranges, histories):
    processed_ships_data = {}
    for ship_id, name, date_range, history in zip(ship_ids, names, date_ranges, histories):
        ship_data = {
            "name": name,
            "dateRange": date_range,
            "rawHistory": history,
            "processedHistory": {}  # Blank placeholder, not necessary, but indicates our intentions
        }
        
        voyages = {}
        ship_info, voyage_string = row["History"].split("Voyages: ")
        processed_history = {}  # The dict we'll eventually assign to ship_data["processedHistory"]
        processed_history["shipInfo"] = ship_info
    
        voyage_numbers = re.findall(r"\(\d{1,2}\)", voyage_string)  # This finds any number in round brackets `(i)`
        raw_voyages = re.split(r"\(\d{1,2}\) ", voyage_string)[1:]  # First item in list is empty string due to split around first bracketed voyage number (1) 
    
        for i, rv in zip(voyage_numbers, raw_voyages):
            voyage = {
                "voyage_number": i,
                "duration": "",
                "destination": "",
                "captain": "",
                "route": []
            }
    
            duration_dest, captain, route_str = rv.split(". ")[:3]
            duration, destination = duration_dest.split(" ")[:2]
    
            voyage["captain"] = captain
            voyage["destination"] = destination
            voyage["duration"] = duration
            voyage["route"] = route_str.split(" - ")
    
            voyages[i] = voyage
        
        processed_history["voyages"] = voyages
        
        ship_data["processedHistory"] = processed_history
        
        # the ship_info dict is now complete, and we can assign it to processed_ships_data
        processed_ships_data[ship_id] = ship_data
    return processed_ships_data

def simple_parse(ship_id, row, date_place_regex="default", place_date_regex="default"):
    if date_place_regex == "default":
        date_place_regex = re.compile(r"(?P<Date>\d{1,2} \w{3}( \d{4})?) (?P<Location>\b[\w\s]*\b)")
    if place_date_regex == "default":
        place_date_regex = re.compile(r"(?P<Location>\b[\w\s]*\b) (?P<Date>\d{1,2} \w{3} \d{4})")
    
    ship_info = {
        "name": row["ShipName"],
        "dateRange": row["DateRange"],
        "shipInfo": "",
        "voyages": {},
        "rawHistory": row["History"]
    }

    voyages = {}
    info, voyage_string = row["History"].split("Voyages: ")
    ship_info["info"] = info.strip()

    voyage_numbers = re.findall(r"\(\d{1,2}\)", voyage_string)  # This finds any number in round brackets `(i)`
    # voyage_numbers = re.findall(r"(?<=\()\d{1,2}(?=\))", voyage_string)  # This finds any number in round brackets `(i)`, and keeps the number
    raw_voyages = re.split(r"\(\d{1,2}\) ", voyage_string)[1:]  # First item in list is empty string due to split around first bracketed voyage number (1) 
    for i, rv in zip(voyage_numbers, raw_voyages):
        voyage_number = int(i[1:-1])
        voyage = {
            "voyage_number": voyage_number,
            "duration": "",
            "destination": "",
            "captain": "",
            "route": []
        }

        duration_dest, captain, route_str = rv.split(". ")[:3]
        duration, destination = duration_dest.split(" ")[:2]

        voyage["captain"] = captain
        voyage["destination"] = destination
        voyage["duration"] = duration

        raw_stops = route_str.split(" - ")
        stops = []
        
        start = place_date_regex.search(raw_stops[0])
        start_location, start_date = start.group("Location"), start.group("Date")
        
        stops.append({start_date: start_location})

        for stop in raw_stops[1:]:
            match = date_place_regex.search(stop)
            loc, date = match.group("Location"), match.group("Date")
            stops.append({date: loc})

        voyage["route"] = stops

        voyages[voyage_number] = voyage

    ship_info["voyages"] = voyages
    
    return ship_info


def complete_parse(ships_df):
    """
    Parser developed to handle the majority of data formats found in the History column of the ships dataset
    """
    place_date_regex = re.compile(r"(?P<Location>[a-zA-Z\s']*\b)? ?(?P<Date>(\d{1,2}\s)?\w{3}(\s\d{4})?)?")
    date_place_regex = re.compile(r"(?P<Date>(\d{1,2}\s)?\w{3}(\s\d{4})?)? ?(?P<Location>\b[a-zA-Z\s'-]*\b)")
    duration_dest_regex = re.compile(r"(?P<Duration>\b[\d/-]*\b) ?(?P<Destination>[\s\w,&--'\(\)]*)?.?$")
    
    ship_voyages = []
    voyage_part_parse_failures = []
    dur_date_failures = []
    date_place_failures = []
    place_date_failures = []
    
    for ship_id, row in ships_df.iterrows():
        ship_info = {
            "name": row["CorporateName"],
            "dates": row["DateRange"],
            "info": "",
            "voyages": [],
            "raw_history": row["History"]
        }
    
        voyages = []
        if type(row["History"]) != str:
            ship_info["info"] = "No history recorded"
            ship_voyages.append({ship_id: ship_info})
            continue
    
        if "Voyages: " in row["History"]:
            info, voyage_string = row["History"].split("Voyages: ")
            ship_info["info"] = info.strip()
        else:  # No voyage information
            ship_info["info"] = row["History"]
            ship_voyages.append({ship_id: ship_info})
            continue
        
        
        raw_voyages = [x.strip() for x in re.split(r"\(\d{1,2}\) ", voyage_string) if x]  # First item in list is empty string due to split around first bracketed voyage number (1) 
        for rv in raw_voyages:
            voyage = {
                "duration": "",
                "start_date": "",
                "end_date": "",
                "destination": "",
                "captain": "",
                "route": [],
                "parse_failure": False
            }
    
            voyage_parts = [x.strip() for x in rv.split(".") if x]           
            try:
                if ("Capt" in rv or "Master" in rv) and "-" in rv:
                    duration_dest, captain, route_str = voyage_parts[:3]
                elif ("Capt" in rv or "Master" in rv) and "-" not in rv:
                    duration_dest, capt = voyage_parts[:2]
                elif "-" in rv:
                    duration_dest, route_str = voyage_parts[:2]
                elif len(voyage_parts) == 2 and "-" not in rv:
                    duration_dest, route_str = voyage_parts
                elif "-" not in rv:
                    duration_dest = rv
            except ValueError:
                voyage_part_parse_failures.append((ship_id, rv))
                voyage["route"].append(rv)
                voyage["parse_failure"] = True
                voyages.append(voyage)
                continue
    
            try:
                dd_match = duration_dest_regex.match(duration_dest)
                duration, destination = dd_match.group("Duration"), dd_match.group("Destination")
            except AttributeError as e:
                dur_date_failures.append((ship_id, duration_dest))
                voyage["route"].append(rv)
                voyage["parse_failure"] = True
                voyages.append(voyage)
                continue
    
            voyage["captain"] = captain
            voyage["duration"] = duration
            voyage["destination"] = destination
    
            raw_stops = route_str.split(" - ")
            stops = []
    
            try:
                start = place_date_regex.search(raw_stops[0])
                start_location, start_date = start.group("Location"), start.group("Date")
                if start_location:
                    start_location = start_location.strip()
            except AttributeError:
                stops.append({"Unparsed stop": stop})
                voyage["parse_failure"] = True
                place_date_failures.append((ship_id, raw_stops[0]))
                
            voyage["start_date"] = start_date
            
            stops.append({start_date: start_location})
    
            for stop in raw_stops[1:]:
                dp_match = date_place_regex.match(stop)
                if dp_match:
                    loc, date = dp_match.group("Location").strip(), dp_match.group("Date")
                    stops.append({date: loc})
                elif not date and re.search(r"\d", stop):  # Check if it's actually place/date format
                    pd_match = place_date_regex.match(stop)
                    pd_loc, pd_date = pd_match.group("Location").strip(), pd_match.group("Date")
                    if pd_date:
                        loc, date = pd_loc, pd_date
                        stops.append({date: loc})
                    else:
                        date_place_failures.append((ship_id, stop))
                        stops.append({"unable_to_date": stop})
                        voyage["parse_failure"] = True                       
                else:
                    date_place_failures.append((ship_id, stop))
                    stops.append({"unable_to_date": stop})
                    voyage["parse_failure"] = True    
    
            if len(voyage_parts) > 3:
                [stops.append({"Additional voyage": p}) for p in voyage_parts[3:]]
                
            voyage["route"] = stops
            voyage["end_date"] = [x for x in stops[-1].keys()][0]
    
            voyages.append(voyage)
    
        ship_info["voyages"] = voyages
    
        ship_voyages.append({ship_id: ship_info})

    return ship_voyages, voyage_part_parse_failures, dur_date_failures, date_place_failures, place_date_failures


def to_json(ships, f):
    ship_dict = {}
    for s in ships:
        ship_dict |= s

    with open(f, "w") as f:
        json.dump(ship_dict, f, indent="\t")


def from_json(fp):
    with open(fp, "r") as f:
        ship_dict = json.load(f)

    return [{k:v} for k,v in ship_dict.items()]



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
    ships_df = ah_df[["CorporateName", "History", "DateRange"]].rename(columns={"CorporateName": "ShipName"}).rename_axis(index="RecordID")
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

    sample_df = ships_df.loc[ground_truth_index]
    return sample_df


def main():
    """
    Main function to convert raw xlsx data to csv ready for use in teaching
    :return:
    """
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
