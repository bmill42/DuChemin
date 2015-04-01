import sys, os, random, csv

if __name__ == "__main__":
 try:
  rows, cols  = map(int, sys.argv[1].lower().split("x"))
  file_name = sys.argv[2]
 except:
  print "Proper usage: python ./random_CSV_writer.py NxM file_output.csv\n"
  sys.exit(0)

 #Construct the random matrix.
 random_matrix = [[random.randint(-25,25) for j in xrange(cols)] for i in xrange(rows)]
 random_matrix = [["heading_{}".format(i) for i in xrange(cols)]]+random_matrix 

 out = csv.writer(open(file_name,"w"), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
 for row in random_matrix:
  out.writerow(row)

 print "Random matrix constructed!"
