#!/usr/bin/env python
"""
This program does three things:
1. Opens a zip file
2. Extracts all the ontology use information from each file in the zip file
3. Repeats 1 and 2 for every zip file in the designated directory 

A handy rundown on tarfiles (and the like) in python: http://pymotw.com/2/tarfile/index.html
"""

#import sys
#print('\n'.join(sorted(sys.path)))

print "BEGIN"

import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager
def rdfNamespaceProcessor(filename, fyle):
    g=Graph()
    g.parse(fyle ,format=rdflib.util.guess_format(filename))
    #print filename, str(len(g))
    #for ns in g.namespaces():
    #    print ns
    predicates = g.query("""SELECT DISTINCT ?p WHERE {?s ?p ?o}""")
    objects = g.query("""SELECT DISTINCT ?o WHERE {?s ?p ?o}""")
    po_list = [predicates,objects,g.namespaces()]
    #print po_list
    return po_list


from rdflib import URIRef
def printToFiles(filename, po_list, predicates_out, objects_out, combined_out, counts_out):
    nscount = 0
    pcount = 0
    ocount = 0
    #print "PO_LIST[2]"
    #print po_list[2]
    for ns in po_list[2]:
        nscount += 1
        #print ns
        for p in po_list[0]:
            if ns[1] in p[0]:
                pcount += 1
                predicates_out.write(filename + "," + p[0] + "\n")
                combined_out.write(filename + "," + ns[1] + "," + ns[0] + "," + p[0][len(ns[1]):] + "\n")
        for o in po_list[1]:
            if ns[1] in o[0][:len(ns[1])]:
                ocount += 1
                objects_out.write(filename + "," + o[0] + "\n")
                combined_out.write(filename + "," + ns[1] + "," + ns[0] + "," + o[0][len(ns[1]):] + "\n")
    counts_out.write(filename + "," + str(nscount) + "," + str(pcount) + "," + str(ocount) + "\n")
    counts_out.flush()
    #print filename + "," + str(nscount) + "," + str(pcount) + "," + str(ocount)
    """
    if "http://" in o[0][0:7]:
        print o
        objects_out.write(filename + "," + o[0] + "\n")
    """
    pass


mypath="/Users/jsimpson/Documents/workspace/NJVRprocessing/"
#Find all the files in a directory (general process from http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python )
from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
print onlyfiles

#Read a tarfile (general process from http://stackoverflow.com/questions/11482342/read-a-large-zipped-text-file-line-by-line-in-python ) 
import tarfile
with open("predicate_out.csv","w") as predicates_out, open("objects_out.csv", "w") as objects_out, open("combined_out.csv", "w") as combined_out, open("counts_out.csv", "w") as counts_out, open("exceptions.txt", "w") as exceptions:
    predicates_out.write("file,property\n")
    objects_out.write("file,property\n")
    combined_out.write("file,namespaceURL,label,attribute\n")
    counts_out.write("file,numberOfNamespaces,numberOfProperties,numberOfClasses\n")
    for zipfile in onlyfiles:
        if "tar" in zipfile:
            with tarfile.open(zipfile, mode='r:*') as z:
                print zipfile
                #print z.getnames()
                for filename in z.getnames():
                    if "rdf" in filename:
                        fyle = z.extractfile(filename)
                        try:
                            po_list = rdfNamespaceProcessor(filename, fyle)
                            printToFiles(filename, po_list, predicates_out, objects_out, combined_out, counts_out)
                        except:
                            exceptions.write(filename + "\n")
                            exceptions.flush()
print "END"

