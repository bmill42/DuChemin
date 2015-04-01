#!/usr/bin/python

"""
Here, you should put your linear regression analysis, i.e., the functions you
need to go through the data and find interesting linearly related variables
(pairs that have small residuals).  You should feel free to use the numpy
linear regression function to do the calculation for you.  For information on
the numpy linear regression function see:
http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html
"""
import sys, json, time
from numpy import array, linalg, ones, mean
from get_data import *


def get_linear_regressions(headers, data_list, calc_r2 = False):
 #Variable Setup.

 data_dict = get_data_dict(headers, data_list) #Sort by column.

 data_regressions = {}
 r2_dict = {}
 i = 1

 #Perform a linear regression against each column.
 for field in headers:

  #Get the A matrix -- that is, the matrix where the first term is [x_1, 1]
  specific_col = array(data_dict[field])
  A = array([specific_col, ones(len(specific_col))])

  #Iterate through the header combinations that were not already compared.
  for j in xrange(i, len(headers)):
   other_field = headers[j]

   #Actually perform the Linear Regression (in the form Ax=y)
   y = array(data_dict[other_field])
   regressed_array = linalg.lstsq(A.T, y)

   #Store the Linear Regression
   data_regressions["{} --> {}".format(field, other_field)]=regressed_array[0]

   if calc_r2:
    r2_dict["{} --> {}".format(field, other_field)]=get_r2(y, regressed_array[1])

  i += 1
 return data_regressions, r2_dict

def get_r2(column_array, residual):
 return 1 - (residual / (column_array.size * column_array.var()))[0]

def arrayDict_to_listDict(arrayDict):
 return {key:val.tolist() for key,val in arrayDict.iteritems()}
 
