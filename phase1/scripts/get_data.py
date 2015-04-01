#!/usr/bin/python

import csv

#Global Variable Setup.
col_std_devs = []
col_means = []
col_sums = []
cols_to_remove = []
cols_checked = False


def is_number(num):
 try:
  float(num)
  return True
 except Exception as e:
  return False

def clean_row(row):
 #Variable Setup
 global cols_checked
 global cols_to_remove

 #If any element is missing, replace it with its mean.
 row = [row[i] if (row[i] and row[i]!="?") else col_means[i] for i in xrange(len(row))]

 #Purge any non-number columns (based on the first row). #TODO: Check the first x in case of any outliers that may exist in the first row.
 if not cols_checked:
  cols_to_remove = [i for i in xrange(len(row)) if not is_number(row[i])]
  cols_checked = True

 for col in cols_to_remove:
  row.pop(col)
 
 for element in row:
  if not is_number(element):
   return None 
 return map(float, row)

def get_col_sums(data):
 global col_sums

 #If the col_sums were already calculated, just return them.
 if col_sums:
  return col_sums

 #Clean the data by replacing empty/unknown cells with averages.
 col_sums = [0 for i in xrange(len(data))]
 for row in data:
  for i in xrange(len(row)):
   if is_number(row[i]):
    col_sums[i] += float(row[i])

 return col_sums

def get_col_means(data):
 global col_means
 
 #If the means were already calculated, just return them.
 if col_means:
  return col_means

 for col in get_col_sums(data): 
  col_means = [float(col)/len(data) for col in col_sums]

 return col_means

def get_col_std_devs(data):
 global col_std_devs
 
 #If the standard deviations were already calculated, just return them.
 if col_std_devs:
  return col_std_devs

 #Variable setup
 col_length = len(data) #IE: Number of entries in the columns.
 row_range = xrange(len(data[0])) #IE: Range 1..n for the length n of a row.
 col_means = get_col_means(data) #The mean value for each column.

 col_diffs = [0]*len(data[0])
 for row in data:
  for i in row_range:
   col_diffs[i] += (float(row[i])-col_means[i])**2

 col_std_devs = [(col_diffs[i]/col_length)**0.5 for i in row_range]

 return col_std_devs

#Convert the CSV into a list of lists (rows).
def get_data_list(csv_file, clean=False, normalize=False, force_ints=False):
 with open(csv_file) as f:
  #Variable Setup
  f_csv = csv.reader(f)
  data_list = []
  headers = next(f_csv) #Skip a row to accomodate the headers.
  dirty_data = [row for row in f_csv]

  #Clean the data if necessary.
  if clean:
   #Calculate the column means.
   col_means = get_col_means(dirty_data)

   for row in dirty_data:
    cleaned_row = clean_row(row)   
    if cleaned_row:
     data_list.append(cleaned_row)

  if normalize:
   #Calculate the column means.
   col_means = get_col_means(dirty_data)
   col_std_devs = get_col_std_devs(dirty_data)

   if not data_list:
    data_list = dirty_data
    
   row_range = xrange(len(headers))
   col_length = len(dirty_data)
   data_dict = get_data_dict(headers, data_list)
    
   data_list = [[(float(row[i])-col_means[i])/col_std_devs[i] for i in row_range] for row in data_list]
   return data_list


  if data_list:
   return data_list

  if force_ints:
    return [map(float, row) for row in dirty_data]
    
  return dirty_data

def get_data_without_cols(csv_file, cols_to_remove):
 with open(csv_file) as f:
  f_csv = csv.reader(f)
  return [[row[i] for i in xrange(len(row)) if i not in cols_to_remove] for row in f_csv]

def get_data_only_with_cols(csv_file, cols_to_keep):
 with open(csv_file) as f:
  f_csv = csv.reader(f)
  whitelist = set(cols_to_keep) 
  #Allow one-based indexing.
  return [[row[i] for i in xrange(len(row)) if (i) in whitelist] for row in f_csv]

def get_data_dict(headers, data_list):
 #Apply the headers to the data dicts.
 data_dict = {header:[] for header in headers}
 #Apply the data to the header.
 for row in data_list:
  for field, val in zip(headers, row):
   data_dict[field].append(val)
 return data_dict

def get_headers(csv_file):
 global cols_to_remove 
 with open(csv_file) as f:
  f_csv = csv.reader(f)
  headers = next(f_csv)
 #Remove any headings that were removed in the cleaning process.
 for col in cols_to_remove:
  headers.pop(col)
 return headers

def write_data(filename, headers, rows_list_of_lists):
    with open(filename,'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(rows_list_of_lists)

if __name__ == "__main__": _test()	
