from sys import path
from scipy.spatial.distance import euclidean as d_eucli

import matplotlib.pyplot as plt

path.insert(0, './hotSAX')
from sax import sax, list_ts_to_list_paa
path.insert(0, '../')

path.insert(0, './iSAX_v0_3')
from tree_iSAX import Tree_iSAX
path.insert(0, '../')

import pandas as pd
from queue import PriorityQueue as pqueue
import time
import csv

slash = "\\"
from sys import platform

if platform == "linux" or platform == "linux2":
    slash = '/'

print(slash)
# fonction permettant de convertir str provenant des csv en datetime64[ns]
def dateparse (d):
    return pd.to_datetime(d)
st_leu = pd.read_csv('../SaintLeu_2014_2015'+slash+'saintleu_2014_2015.csv', parse_dates=['Timestamp'],date_parser=dateparse)


mon_arbre_24 = Tree_iSAX(size_word=10, threshold=20, data_ts=st_leu['Text_Avg'].values.tolist())
print("len(st_leu['Text_Avg'].values.tolist()) : ", len(st_leu['Text_Avg'].values.tolist()))

nbr_ts = 0
# sur la premiere annee
for i in range(0,525600,72):
    start = i
    end = start + 60*24
    mon_arbre_24.insert(st_leu['Text_Avg'][start:end])
    nbr_ts += 1


from anytree import Node, RenderTree

nbr_node = 0
nbr_leaf = 0
for pre, fill, node in RenderTree(mon_arbre_24.root):
    print("%s%s" % (pre, node.name))
    nbr_node += 1
    if node.is_leaf:
        nbr_leaf += 1


print(nbr_node)
print(nbr_leaf)
print(nbr_ts)
print(" ")

for i in range(0, mon_arbre_24.size_word):
    print("split ", i, " = ", mon_arbre_24.root.cmpt_seg_split.count(i))


start_time = time.time()
pq = pqueue()
# Pour la seconde annee
# for i in range(525600,len(st_leu['Text_Avg'].values.tolist()),72):
# 20 jrs qui se suivent mais qui ne se chevauchent pas
nbr_st = 240
nbr_knn = 10
for i in range(525600, 525600 + 60*24*nbr_st, int(60*24/24) ):
    start = i
    end = start + 60*24
    mynodes = mon_arbre_24.exactSearch(st_leu['Text_Avg'][start:end], knn=nbr_knn)
    sum_dist = 0
    for j in range(0, 10):
        sum_dist += d_eucli(mynodes[j].st.tolist(), st_leu['Text_Avg'][start:end].tolist() )
    pq.put((sum_dist, st_leu['Text_Avg'][start:end].tolist(), st_leu['Timestamp'][start] ))

dist_list = []
with open('result/priotab_st'+str(nbr_st)+'_knn'+str(nbr_knn)+'_chev3.csv', 'w', newline='') as csvfile1:
    with open('result/distlist_st'+str(nbr_st)+'_knn'+str(nbr_knn)+'_chev3.csv', 'w', newline='') as csvfile2:
        priotab = csv.writer(csvfile1, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        distlist = csv.writer(csvfile2, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        print(pq)
        while not pq.empty():
            next = pq.get()
            print(next[0])
            distlist.writerow([next[0], next[2]])
            print(next[1])
            priotab.writerow(next[1])

print("--- %s seconds ---" % (time.time() - start_time))

