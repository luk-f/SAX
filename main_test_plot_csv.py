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
import matplotlib.pyplot as plt

slash = "\\"
from sys import platform

if platform == "linux" or platform == "linux2":
    slash = '/'

print(slash)
# fonction permettant de convertir str provenant des csv en datetime64[ns]
def dateparse (d):
    return pd.to_datetime(d)

nbr_st = 60
nbr_knn = 20

#test_st240_knn10_chev1h
mon_csv = pd.read_csv('result/priotab_st240_knn10_chev12.csv', header=None, lineterminator='\n', sep=' ')
#mon_csv = pd.read_csv('result/priotab_st'+str(nbr_st)+'_knn'+str(nbr_knn)+'.csv', header=None, lineterminator='\n', sep=' ')


print(mon_csv.values.tolist())

#taille de la figure
fig = plt.figure(figsize=(25, 5))

#permet de mettre figure cote à cote
ax1 = fig.add_subplot(1,2,1)
# boite a moustache
# ax1.boxplot(data1)
# for i in range(len(mon_csv)):
for i in range(0, 10):
    print(mon_csv.values.tolist()[i])
    ax1.plot(mon_csv.values.tolist()[i])

# permet de mettre figure cote à cote

ax2 = fig.add_subplot(1,2,2)
for i in range(len(mon_csv.values.tolist())-11,len(mon_csv.values.tolist()) ):
    ax2.plot(mon_csv.values.tolist()[i])


plt.show()
