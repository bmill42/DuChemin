from manage import *
import csv
import re
import operator
import pprint

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
	
def adjacent_cadences_by_piece(csv_input, csv_output):
	headers = get_headers(csv_input)
	piece_index = headers.index("composition_number")
	phrase_index = headers.index("phrase_number")
	cadence_tone_index = headers.index("cadence_final_tone")
	
	new_headers = []
	
	data = get_data_list(csv_input)
	new_data = []
	piece_data = dict()
	seen_list = []
	pieces = dict() # values are piece identifiers and keys are highest phrase number so far
	deleted = 0
	
	for row in data:
		piece = row[piece_index]
		if piece in seen_list:
			piece_data[piece].append(row)
		else:
			seen_list.append(piece)
			piece_data[piece] = []
			piece_data[piece].append(row)
	
	seen_list = []
	piece_data_sorted = dict()
	for key in piece_data.keys():
		ordered_phrases = sorted(piece_data[key], key=operator.itemgetter(0))
		#pprint.pprint(ordered_phrases)
		for phrase in ordered_phrases:
			if phrase[0][0:5] != key[0:5]:
				print "MISMATCH ERROR"
				print "piece:", key
				print "phrase:", phrase[0]
				ordered_phrases.remove(phrase)
				deleted += 1
		piece_data_sorted[key] = ordered_phrases
	
	most_phrases = len(max(piece_data.values(), key=len))
	print most_phrases
	
	new_headers.append("composition_number")
	headers_added = []
	# find all the ordered pairs of cadences
	for key in piece_data_sorted.keys():
		piece = []
		piece.append(key) # first column is just the piece number
		phrases = piece_data_sorted[key]
		fields_to_pair = ["cadence_final_tone", "cadence_kind", "cadence_alter", "cadence_role_cantz", "cadence_role_tenz"]
		field_indices_to_pair = {headers.index(field)
                               for field in fields_to_pair}
		
		for index in field_indices_to_pair:
			for n in range(most_phrases-1):
				if n < len(phrases)-1:
					first_field = phrases[n][index]
					second_field = phrases[n+1][index]
					pair = str(first_field) + '+' + str(second_field)
					piece.append(pair)
				else:
					piece.append("None")
				
		new_data.append(piece)
	
	for index in field_indices_to_pair:
		for n in range(most_phrases-1):
			new_headers.append(headers[index] + '_' + str(n+1))
	
	write_data(csv_output, new_headers, new_data)
	print "File written successfully!"
	print "Rows Deleted: {}".format(deleted)


keep_specified_cols(["cadence_kind", "cadence_final_tone","composition_number", "phrase_number","cadence_alter","cadence_role_cantz","cadence_role_tenz","start_measure","stop_measure"],"duchemin_all_data_3_12_2015.csv","duchemin_phase2.csv")

purge_rows_with_col_entry("cadence_kind", "duchemin_phase2.csv", "duchemin_phase2.csv", val="None")

purge_rows_with_col_entry("cadence_kind", "duchemin_phase2.csv", "duchemin_phase2.csv", val="NoCadence")

remove_duplicates("duchemin_phase2.csv", "duchemin_phase2.csv")

fill_empty_col("cadence_alter", "duchemin_phase2.csv", "duchemin_phase2.csv", val="None") 

make_field_map("duchemin_phase2.csv", "duchemin_phase2.csv", "cadence_final_tone")

make_field_map("duchemin_phase2.csv", "duchemin_phase2.csv", "cadence_kind")

remove_cadence_conflicts_smart("duchemin_phase2.csv","duchemin_phase2.csv")

add_final_cadence("duchemin_phase2.csv","duchemin_phase2.csv")

adjacent_cadences_by_piece("duchemin_phase2.csv","data/duchemin.production.csv")

make_similarity_JSON("data/duchemin.production.csv", "data/duchemin.similarities.json")

make_options_JSON("data/duchemin.production.csv","data/duchemin.options.json")


