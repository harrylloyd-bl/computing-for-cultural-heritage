def show_mismatches(s1: list[dict], s2: list[dict]):
    """
    Show the mismatches between two lists of dictionaries
    Dictionaries will need to be in the extract_voyages complete parse format
    """
    s1_dict = {}
    s2_dict = {}

    for ship_id in s1:
        s1_dict |= ship_id
    for ship_id in s2:
        s2_dict |= ship_id
    if s1_dict == s2_dict:
        print("Ships are identical")
        return None

    s1_only = s1_dict.keys() - s2_dict.keys()
    if s1_only:
        print(f"Ship IDs only present in first set: {'\n'.join(s1_only)}")
    s2_only = s2_dict.keys() - s2_dict.keys()
    if s2_only:
        print(f"Ship IDs only present in second set: {'\n'.join(s2_only)}")

    print("Differences in information for Ship IDs present in both sets:")
    common_ship_ids = s1_dict.keys() & s2_dict.keys()
    for ship_id in common_ship_ids:  # TODO refactor to check if value is dict/list then recur/use repeatable fn to compare, rather than these nested lists
        s1_ship_info = s1_dict[ship_id]
        s2_ship_info = s2_dict[ship_id]

        if s1_ship_info == s2_ship_info:
            continue

        if s1_ship_info.keys() ^ s2_ship_info.keys():
            print(f"{ship_id} has keys {', '.join(s1_ship_info.keys())} in set 1 and {', '.join(s2_ship_info.keys())} in set 2")
            print(f"The differing keys are {s1_ship_info.keys() ^ s2_ship_info.keys()}")

        common_ship_info = s1_ship_info.keys() & s2_ship_info.keys()
        for ship_key in common_ship_info:
            s1_value, s2_value = s1_ship_info[ship_key], s2_ship_info[ship_key]
            if ship_key != "voyages" and (s1_value != s2_value):
                print(f"Ship {ship_id} has {ship_key}: {s1_value} in set 1 and {ship_key}: {s2_value} in set 2")

            elif ship_key == "voyages" and (s1_value != s2_value):
                s1_voyages, s2_voyages = s1_value, s2_value
                print(f"\n**Ship {ship_id}**")
                if s1_voyages.keys() ^ s2_voyages.keys():
                    print(
                        f"{ship_id} has voyages {', '.join(s1_voyages.keys())} in set 1 and {', '.join(s2_voyages.keys())} in set 2")
                    print(f"The differing voyages are {s1_voyages.keys() ^ s2_voyages.keys()}")

                common_voyages = sorted(list(s1_voyages.keys() & s2_voyages.keys()))
                for voyage_id in common_voyages:
                    v1, v2 = s1_voyages[voyage_id], s2_voyages[voyage_id]
                    if v1 != v2:
                        print(f"\nVoyage {voyage_id}")
                        if v1.keys() ^ v2.keys():
                            print(f"{voyage_id} has keys {', '.join(v1.keys())} in set 1 and {', '.join(v2.keys())} in set 2")
                            print(f"The differing keys are {v1.keys() ^ v2.keys()}")

                        common_voyage_info = v1.keys() & v2.keys()
                        for v_key in common_voyage_info:
                            v1_value, v2_value = v1[v_key], v2[v_key]
                            if v_key != "route" and (v1_value != v2_value):
                                print(f"Voyage {voyage_id} has {v_key}: {v1_value} in set 1 and {v_key}: {v2_value} in set 2")

                            elif v_key == "route" and (v1_value != v2_value):
                                s1_stops, s2_stops = v1_value, v2_value
                                for stop in s1_stops:
                                    if stop not in s2_stops:
                                        print(f"Stop {stop} in set 1 but not in set 2\n")
                                for stop in s2_stops:
                                    if stop not in s1_stops:
                                        print(f"Stop {stop} in set 2 but not in set 1\n")


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "features.csv",
    # -----------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Generating features from dataset...")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")
    logger.success("Features generation complete.")
    # -----------------------------------------


if __name__ == "__main__":
    app()
