#!/usr/bin/python

# Functional Summary: Create KD-tree objects.

from operator import itemgetter
import random

class KDTree(object):
  def __init__(self, heading, value, left=None, right=None):
    self.left = left
    self.right = right
    self.value = value
    self.heading = heading
  def __str__(self):
    left = "\"left\":{}".format(self.left) if self.left else "\"left\":\"0\""
    right = "\"right\":{}".format(self.right) if self.right else "\"right\":\"0\""
    return "{{\"heading\":\"{}\", \"value\":{},{},{}}}".format(self.heading, self.value, left, right)  

#Given a list of lists in a tree-like format (eg: [heading, value, [heading,value, []], heading,value, []] ), return a KDTree obejct.
def KDTree_from_list(lst):
  #Variable Setup
  kd_tree = KDTree(lst[0], lst[1])

  if len(lst)>2:
    kd_tree.left = KDTree_from_list(lst[2])
    if len(lst)==4:
      kd_tree.right = KDTree_from_list(lst[3])
  return kd_tree

#Given a list of lists in a tree-like format (eg: {"heading":"x", "value":20, "left":{"heading":"y", "value":1.4}, "right":{"heading":"y", "value":8.4}} ), return a KDTree obejct.
def KDTree_from_dict(dct):
  return KDTree(dct["heading"], dct["value"], KDTree_from_dict(dct.get("left")), KDTree_from_dict(dct.get("right")))

#Get either the index of the median or (if one does not exist) randomly choose one of two medians given an ordered list.
def get_median_index(lst):
  index = (len(lst)-1)/2
  if len(lst)%2==0:
    return random.choice([index, index+1])  
  return index

#Construct a KDTree by alternating through the dimensions 
def hyperspace_partitioner(headers, header_num, data_list):
  #Headers should "cycle" around when partitioning.
  if header_num == len(headers): header_num = 0

  #Sort the data based on the current header.
  data = sorted(data_list, key=itemgetter(header_num))

  #Get the median index for the data.
  m = get_median_index(data)

  #Child Setup.
  if data[:m]:
    left = hyperspace_partitioner(headers, header_num+1, data[:m])
  else:
    left = None

  if data[m+1:]:
    right = hyperspace_partitioner(headers, header_num+1, data[m+1:])
  else:
    right = None

  #Construct the KD Tree  
  return KDTree(headers[header_num], data[m], left=left, right=right)

