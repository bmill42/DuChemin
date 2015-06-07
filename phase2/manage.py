# !/usr/bin/python

from scripts import *
from operator import itemgetter
# import sys
# import random
import json
import csv
import re
import operator


def filter_R2s(filename, minimum=0, maximum=1, verbose=False):
	with open(filename, "r") as f:
		# Sort the R2 values in descending order.
		R2_dict = json.load(f)
		R2_sorted = sorted([(key, val) for (key, val) in R2_dict.iteritems()],
						   key=itemgetter(1), reverse=True)

		# Filter the R2s.
		R2_filtered = [(key, val) for (key, val) in R2_sorted
					   if (minimum <= val <= maximum)]

		if verbose:
			for (key, val) in R2_filtered:
				print "{}\t--\t{}".format(val, key)

		return R2_filtered


# Return the two column indexes for each element
# of the R2_list in the same order.
def get_R2_columns(R2_list, csv_input):
	with open(csv_input, "r") as f:
		f_csv = csv.reader(f)
		headers = f_csv.next()
		header_set = set(headers)

	# Translate the R2 keys into a tuple for each key.
	R2_cols = []
	for (key, val) in R2_list:
		current_headings = [None, None]
		col_left, col_right = key.split(" --> ")

		# Check that the column exists and add it to the current_headings.
		if col_left in header_set:
			current_headings[0] = headers.index(col_left)
		if col_right in header_set:
			current_headings[1] = headers.index(col_right)

		R2_cols.append(current_headings)
	return R2_cols


def get_col_mean(data, col):
	return sum([float(row[col-1]) for row in data if row[col-1]])/len(data)


def fill_empty_col(field, csv_input, csv_output, val=None):
	try:
		# Variable Setup
		data = get_data_list(csv_input)
		headers = get_headers(csv_input)
		col = headers.index(field)
		if not val:
			val = get_col_mean(data, col)

		# Fill in any empty column entries with the value
		# specified (or mean by default)
		data = [[val if (col == i and row[i] in " None?")
				else row[i] for i in xrange(len(row))] for row in data]
		write_data(csv_output, headers, data)

		print "File written successfully!"
	except Exception as e:
		print "FATAL: File creation failed...\n\t{}".format(e)


def calculate_col_density(field, csv_input, val=""):
	try:
		# Variable Setup.
		data = get_data_list(csv_input)
		headers = get_headers(csv_input)
		col = headers.index(field)
		header = headers.pop(col)
		total = len(data)
		found = 0

		# Calculate the number of empty.
		for entry in data:
			if entry[col] == val:
				found += 1

		print "Header: {}	({})".format(header, col+1)
		print "Value: {}".format(val)
		print "Found: {}".format(found)
		print "Total: {}".format(total)
		print "% of data with value: {}".format(float(found)/total)

	except Exception as e:
		print "Could not count that column. ERROR: {}".format(e)


def purge_rows_with_col_entry(col_name, csv_input, csv_output, val=""):
	try:
		# Variable Setup.
		data = get_data_list(csv_input)
		headers = get_headers(csv_input)
		col = headers.index(col_name)
		new_data = []
		deleted = 0

		# Ignore any row that has a value match in the specified column.
		for row in data:
			if row[col] == val:
				deleted += 1
			else:
				new_data.append(row)

		write_data(csv_output, headers, new_data)
		print "File written successfully!"
		print "Rows Deleted: {}".format(deleted)

	except Exception as e:
		print "ERROR: {}".format(e)


def keep_specified_cols(fields_to_keep, csv_input, csv_output):
	all_headers = get_headers(csv_input)
	cols_to_keep = [all_headers.index(field) for field in fields_to_keep]

	data = get_data_only_with_cols(csv_input, cols_to_keep)
	headers = data.pop(0)
	write_data(csv_output, headers, data)
	print "File written successfully!"


def make_field_map(csv_input, csv_output, field):
	# Variable Setup.
	headers = get_headers(csv_input)

	start_measure_index = headers.index("start_measure")
	stop_measure_index = headers.index("stop_measure")
	id_index = headers.index("composition_number") # changed from "piece"
	index_of_interest = headers.index(field)

	header = headers[index_of_interest]
	headers += ["{}_before".format(header)]
	headers += ["{}_after".format(header)]

	data = get_data_list(csv_input)
	data_by_composition = {row[id_index]: [] for row in data}
	# Phrases 1 measure off of the end are seen as connected.
	measure_threshhold = 1

	# Sort (ascending) the individual entries for each
	# composition by the first element.
	for i, row in enumerate(data):
		row += [[], []]
		composition = row[id_index]
		data_by_composition[composition].append([i, row])
		data_by_composition[composition].sort(key=lambda x:
											  int(x[1][start_measure_index]))

	for (composition, entries) in data_by_composition.iteritems():
		for i, (row_id, entry) in enumerate(entries):
			if i + 1 == len(entries):  # Don't add an edge for the last node.
				break

			# Variable Setup.
			stop_measure = int(entry[stop_measure_index])
			next_true_start = 0

			for temp_row_id, temp_entry in entries[i+1:]:
				# Variable Setup.
				temp_start_measure = int(temp_entry[start_measure_index])

				if temp_start_measure < stop_measure:
					continue

				if next_true_start == 0:
					next_true_start = temp_start_measure

				# Find the all phrases that start
				# IMMEDIATELY AFTER this phrase stops.
				if next_true_start+measure_threshhold < temp_start_measure:
					break

				# Set the "after" field of this entry.
				if data[row_id][-1] == []:
					data[row_id][-1].append(data[temp_row_id][index_of_interest])

				# Set the "before" field of the later entries.
				if data[temp_row_id][-2] == []:
					data[temp_row_id][-2].append(data[row_id][index_of_interest])

	# Split the "list" entries by "+" to avoid issues reading the CSV.
	for row in data:
		row[-1] = "+".join(row[-1])
		row[-2] = "+".join(row[-2])
		if not row[-1]:
			row[-1] = "None"
		if not row[-2]:
			row[-2] = "None"

	write_data(csv_output, headers, data)
	print "File written successfully! Added 'before' and 'after' for {}".format(header)
	
def rows_similar(row1, row2, headers):
	# Variable Setup.
	lenIndex = headers.index("piece_length")
	threshhold = int(len(headers) * 0.75)  # Number of entries that must be similar.
	num_matches = 0
	# inverse of the ratio of this piece's length to the longest piece (hard-coded as 11)
	lenWeight = 11 / float(row1[lenIndex])  

	for i in range(len(row1)):
		for j in range(len(row2)):
			if headers[i] == headers[j]:
				if headers[i] != "piece_length":
					if row1[i] == row2[j] and row1[i] != "None":
						num_matches += 1
						
	num_matches *= lenWeight
	return num_matches > threshhold


def add_phrase_length(csv_input, csv_output):
	headers = get_headers(csv_input)
	data = get_data_list(csv_input)

	# Get the phrase_length.
	start_col = headers.index("start_measure")
	stop_col = headers.index("stop_measure")

	# Actually add the phrase_length to each row.
	new_data = [row + [int(row[stop_col]) - int(row[start_col]) + 1]
				for row in data]

	write_data(csv_output, headers+["phrase_length"], new_data)
	print "File written successfully!"


def make_similarity_JSON(csv_input, output_file):
	# Variable Setup
	headers = get_headers(csv_input)
	data = [[i] + row for i, row in enumerate(get_data_list(csv_input))]
	adjacency_dict = [[] for row in data]

	# Compare each pair of rows to see if there are similar fields
	for row in data:
		i = row[0]
		for other_row in data[i+1:]:
			j = other_row[0]
			if rows_similar(row[1:], other_row[1:], headers):
				adjacency_dict[i].append(j)
				adjacency_dict[j].append(i)	 # Not needed if bidirectional

	with open(output_file, "w") as f:
		json.dump(adjacency_dict, f)
		print ("File constructed successfully!")


def make_naive_piece_map(csv_input, output_file):
	# Variable Setup.
	headers = get_headers(csv_input)
	data = get_data_list(csv_input)
	adjacency_list = [[] for row in data]
	start_measure_index = headers.index("start_measure")

	# Create a blank list for each piece.
	comp_id = headers.index("piece")
	data_by_composition = {row[comp_id]: [] for row in data}

	# Sort (ascending) the individual entries for each composition
	# by the first element.
	for i, row in enumerate(data):
		composition = row[comp_id]
		data_by_composition[composition].append([i, row])
		data_by_composition[composition].sort(key=lambda x:
											  int(x[1][start_measure_index]))

	# Variable Setup.
	comp_list = data_by_composition.keys()
	last_comp_id = len(comp_list)-1
	comp_id = 0

	for (composition, entries) in data_by_composition.iteritems():
		relative_row_id = 0
		for (row_id, entry) in entries:
			# Don't add an edge for the last node.
			if relative_row_id >= len(entries) - 1:
				continue

			# Grab the next entry.
			next_entry_id = entries[relative_row_id+1][0]

			# Attach the first entry of each composition.
			if relative_row_id == 0:
				other_comp = (comp_list[0] if comp_id == last_comp_id
							  else comp_list[comp_id + 1])
				other_comp_entries = data_by_composition[other_comp]
				other_comp_entry_id = other_comp_entries[0][0]
				adjacency_list[row_id].append(other_comp_entry_id)
				adjacency_list[other_comp_entry_id].append(row_id)

				# Also add the next phrase for the music to this node.
			adjacency_list[row_id].append(next_entry_id)

			relative_row_id += 1
		comp_id += 1

	with open(output_file, "w") as f:
		json.dump(adjacency_list, f)
		print ("File constructed successfully!")


def make_smart_piece_map(csv_input, output_file):
	# Variable Setup.
	headers = get_headers(csv_input)

	start_measure_index = headers.index("start_measure")
	stop_measure_index = headers.index("stop_measure")
	id_index = headers.index("composition_number") # changed from 'piece'

	data = get_data_list(csv_input)
	data_by_composition = {row[id_index]: [] for row in data}
	adjacency_list = [[] for row in data]
	# Phrases 1 measure off of the end are seen as connected.
	measure_threshhold = 1

	# Sort (ascending) the individual entries for
	# each composition by the first element.
	for i, row in enumerate(data):
		row += [[], []]
		composition = row[id_index]
		data_by_composition[composition].append([i, row])
		data_by_composition[composition].sort(key=lambda x:
											  int(x[1][start_measure_index]))

	for (composition, entries) in data_by_composition.iteritems():
		for i, (row_id, entry) in enumerate(entries):
			# Don't add an edge for the last node.
			if i + 1 == len(entries):
				break

			# Variable Setup.
			stop_measure = int(entry[stop_measure_index])
			next_true_start = 0

			for temp_row_id, temp_entry in entries[i+1:]:
				# Variable Setup.
				temp_start_measure = int(temp_entry[start_measure_index])

				if temp_start_measure < stop_measure:
					continue

				if next_true_start == 0:
					next_true_start = temp_start_measure
				# Find the all phrases that start IMMEDIATELY AFTER
				# this phrase stops.
				if next_true_start+measure_threshhold < temp_start_measure:
					break

				adjacency_list[row_id].append(temp_row_id)

	with open(output_file, "w") as f:
		json.dump(adjacency_list, f)
		print ("File constructed successfully!")

def remove_cadence_conflicts(csv_input, csv_output):
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
	final_cad_index = headers.index("final_cadence")
	
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
			piece_data[piece].append([int(re.search(r'[0-9]+\.([1-9][0-9]?):', row[phrase_index]).group(1))] + row)
		else:
			seen_list.append(piece)
			piece_data[piece] = []
			piece_data[piece].append([int(re.search(r'[0-9]+\.([1-9][0-9]?):', row[phrase_index]).group(1))] + row)
	
	seen_list = []
	piece_data_sorted = dict()
	for key in piece_data.keys():
		ordered_phrases = sorted(piece_data[key], key=operator.itemgetter(0))
		for p in range(len(ordered_phrases)):
			ordered_phrases[p].pop(0)
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
		
		# note that this length is the total number of phrases in the piece,
		# regardless of how many of those phrases have cadences.
		# i.e. there may be less than this number of populated columns in the
		# resulting csv file.
		#length_in_phrases = int(re.search(r'[0-9]+\.([1-9][0-9]?):', phrases[-1][0]).group(1))
		
		# this length calculation uses only the number of actual cadences, and will thus match
		# the number of column entries for each piece.
		length_in_phrases = len(phrases)
		
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
		
		# add final cadence here
		for row in data:
			if row[piece_index] == key:
				piece.append(row[final_cad_index])
				break
		# add piece length here
		piece.append(length_in_phrases)
		
		new_data.append(piece)
	
	for index in field_indices_to_pair:
		for n in range(most_phrases-1):
			#new_headers.append(headers[index] + '_' + str(n+1))
			new_headers.append(headers[index])
	new_headers.append("final_cadence")
	new_headers.append("piece_length")
	
	write_data(csv_output, new_headers, new_data)
	print "File written successfully!"
	print "Rows Deleted: {}".format(deleted)

def remove_duplicates(csv_input, csv_output):
	# Variable Setup.
	# headers = get_headers(csv_input)
	data = get_data_list(csv_input)
	cleaned_data = []
	data_set = set()
	duplicates = 0

	for row in data:
		if str(row) not in data_set:
			cleaned_data.append(row)
			data_set.add(str(row))
		else:
			duplicates += 1

	print ("Found {} duplicates!\nFile write complete!").format(duplicates)
	write_data(csv_output, get_headers(csv_input), cleaned_data)


def switch_cols(csv_input, csv_output, c1, c2):
	# Variable Setup.
	headers = get_headers(csv_input)
	data = get_data_list(csv_input)

	if c1 < c2:
		first = c2
		last = c1
	else:
		first = c1
		last = c2

	new_data = [row[:c1] + [row[first]] + row[c1+1:c2] + [row[last]] +
				row[c2+1:] for row in data]
	new_headers = (headers[:c1] + [headers[first]] + headers[c1+1:c2] +
				   [headers[last]] + headers[c2+1:])

	write_data(csv_output, new_headers, new_data)


def count_rows(csv_input):
	data = get_data_list(csv_input)
	rows = len(data)
	cols = len(data[0])
	print "Found {} rows and {} columns!".format(rows, cols)


def count_options(csv_input, row_name):
	# Variable Setup
	data = get_data_list(csv_input)
	headers = get_headers(csv_input)
	row_index = headers.index(row_name)

	option_set = {row[row_index] for row in data}

	print "Found {} options for `{}`!".format(len(option_set), row_name)


def make_options_JSON(csv_input, output_file):
	# Variable Setup
	data = get_data_list(csv_input)	 # Hardcoded to ignore pieces.
	headers = get_headers(csv_input)[1:]
	
	#pair_headers = ["cadence_kind", "cadence_alter", "cadence_role_cantz", "cadence_role_tenz", "cadence_final_tone", "final_cadence"] # hardcoded to use the headers that were paired
	
	option_dict = {header: [] for header in headers}

	for row in data:
		for header in headers:
			option_list = []
			for col_index in range(1,len(headers)+1):
				if headers[col_index-1] == header and row[col_index] not in option_list and row[col_index] != "None":
					option_list.append(row[col_index])
			option_dict[header] += [opt for opt in option_list if opt not in option_dict[header]]
	for key in option_dict.keys():
		option_dict[key] = set(option_dict[key])
	
	#print option_dict
	serialized_dict = {key: list(vals)
					   for key, vals in option_dict.iteritems()}

	with open(output_file, "w") as f:
		json.dump(serialized_dict, f)
		print ("File constructed successfully!")
