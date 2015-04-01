from manage import *
import csv
import re

def remove_cadence_conflicts(csv_input, csv_output):
	headers = get_headers(csv_input)
	piece_index = headers.index("composition_number")
	phrase_index = headers.index("phrase_number")
	
	data = get_data_list(csv_input)
	new_data = []
	seen_list = []
	deleted = 0
	
	for i, row in enumerate(data):
		piece = row[piece_index]
		phrase = row[phrase_index]
		if [piece, phrase] in seen_list:
			deleted += 1
		else:
			seen_list.append([piece, phrase])
			new_data.append(row)
	
	write_data(csv_output, headers, new_data)
	print "File written successfully!"
	print "Rows Deleted: {}".format(deleted)
		
def remove_cadence_conflicts_smart(csv_input, csv_output):
	headers = get_headers(csv_input)
	piece_index = headers.index("composition_number")
	phrase_index = headers.index("phrase_number")
	end_measure_index = headers.index("stop_measure")
	
	data = get_data_list(csv_input)
	new_data = []
	phrase_list = []
	deleted = 0
	
	phrase_hi_meas = dict()
	phrase_last_added_row = dict()
	for row in data:
		phrase = row[phrase_index]
		if phrase in phrase_list:
			if row[end_measure_index] > phrase_hi_meas[phrase]:
				phrase_hi_meas[phrase] = row[end_measure_index]
				new_data.remove(phrase_last_added_row[phrase])
				deleted += 1
				new_data.append(row)
				phrase_last_added_row[phrase] = row
			else:
				deleted += 1
		else:
			phrase_list.append(phrase)
			new_data.append(row)
			phrase_hi_meas[phrase] = row[end_measure_index]	
			phrase_last_added_row[phrase] = row
	
	write_data(csv_output, headers, new_data)
	print "File written successfully!"
	print "Rows Deleted: {}".format(deleted)
	
def add_final_cadence(csv_input, csv_output):
	headers = get_headers(csv_input)
	piece_index = headers.index("composition_number")
	phrase_index = headers.index("phrase_number")
	cadence_tone_index = headers.index("cadence_final_tone")
	
	headers += ["{}".format("final_cadence")]
	
	data = get_data_list(csv_input)
	new_data = []
	seen_list = []
	pieces = dict() # values are piece identifiers and keys are highest phrase number so far

	deleted = 0
	
	for i, row in enumerate(data):
		piece = row[piece_index]
		phrase = row[phrase_index]
		cadence_tone = row[cadence_tone_index]
		if piece in seen_list:
			thisphrase = re.search('(DC[0-9]+\.)([0-9]+):.+',phrase)
			phrase_number = int(thisphrase.group(2))
			if phrase_number > pieces[piece]:
				pieces[piece] = [phrase_number, cadence_tone]
		else:
			seen_list.append(piece)
			thisphrase = re.search('(DC[0-9]+\.)([0-9]+):.+',phrase)
			phrase_number = int(thisphrase.group(2))
			pieces[piece] = [phrase_number, cadence_tone]
	
	for row in data:
		piece = row[piece_index]
		new_row = row + [pieces[piece][1]]
		new_data.append(new_row)
	
	write_data(csv_output, headers, new_data)
	print "File written successfully!"
	


keep_specified_cols(["cadence_kind", "cadence_final_tone","composition_number", "phrase_number","cadence_alter","cadence_role_cantz","cadence_role_tenz","start_measure","stop_measure"],"duchemin_all_data_3_9_2015.csv","duchemin_feature_selected2-test.csv")

purge_rows_with_col_entry("cadence_kind", "duchemin_feature_selected2-test.csv", "duchemin_feature_selected2-test.csv", val="None")

purge_rows_with_col_entry("cadence_kind", "duchemin_feature_selected2-test.csv", "duchemin_feature_selected2-test.csv", val="NoCadence")

remove_duplicates("duchemin_feature_selected2-test.csv", "duchemin_feature_selected2-test.csv")

make_field_map("duchemin_feature_selected2-test.csv", "duchemin_feature_selected_map.csv", "cadence_final_tone")

make_field_map("duchemin_feature_selected_map.csv", "duchemin_feature_selected_map.csv", "cadence_kind")

remove_cadence_conflicts_smart("duchemin_feature_selected_map.csv","duchemin_feature_selected_map_pruned.csv")

add_final_cadence("duchemin_feature_selected_map_pruned.csv","data/duchemin.production.csv")

make_smart_piece_map("data/duchemin.production.csv", "data/duchemin.map.json")

make_similarity_JSON("data/duchemin.production.csv", "data/duchemin.similarities.json")

#keep_specified_cols(["cadence_kind", "cadence_final_tone","composition_number", "phrase_number","cadence_alter","cadence_role_cantz","cadence_role_tenz","final_cadence","cadence_kind_before","cadence_kind_after","cadence_final_tone_before","cadence_final_tone_after"],"data/duchemin.production.csv","data/duchemin.production.csv")

make_options_JSON("data/duchemin.production.csv","data/duchemin.options.json")


