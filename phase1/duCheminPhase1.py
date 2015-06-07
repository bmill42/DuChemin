from manage import *

keep_specified_cols(["cadence_kind", "cadence_final_tone","composition_number", "phrase_number","cadence_alter","cadence_role_cantz","cadence_role_tenz","start_measure","stop_measure"],"duchemin_all_data_5_12_2015.csv","data/duchemin.production.csv")

purge_rows_with_col_entry("cadence_kind", "data/duchemin.production.csv", "data/duchemin.production.csv", val="None")

purge_rows_with_col_entry("cadence_kind", "data/duchemin.production.csv", "data/duchemin.production.csv", val="NoCadence")

remove_duplicates("data/duchemin.production.csv", "data/duchemin.production.csv")

make_field_map("data/duchemin.production.csv", "data/duchemin.production.csv", "cadence_final_tone")

make_field_map("data/duchemin.production.csv", "data/duchemin.production.csv", "cadence_kind")

remove_cadence_conflicts_smart("data/duchemin.production.csv","data/duchemin.production.csv")

add_final_cadence("data/duchemin.production.csv","data/duchemin.production.csv")

make_smart_piece_map("data/duchemin.production.csv", "data/duchemin.map.json")

make_similarity_JSON("data/duchemin.production.csv", "data/duchemin.similarities.json")

# comment out this line to make start_ and stop_measure options in the pulldown
keep_specified_cols(["cadence_kind", "cadence_final_tone","composition_number", "phrase_number","cadence_alter","cadence_role_cantz","cadence_role_tenz","final_cadence","cadence_kind_before","cadence_kind_after","cadence_final_tone_before","cadence_final_tone_after"],"data/duchemin.production.csv","data/duchemin.production.csv")

make_options_JSON("data/duchemin.production.csv","data/duchemin.options.json")


