from node import RootNode, InternalNode, TerminalNode

from numpy import amax, amin, argmin, linspace, sqrt
from scipy.integrate import quad
from matplotlib import pyplot as plt
from scipy.stats import norm
from copy import deepcopy

from sys import path
path.insert(0, './hotSAX')
from sax import breakpoints
from gaussian import gaussian, NormalGaussian
path.insert(0, '../')

from warnings import warn

"""
La classe Tree_iSAX contenant val pour breakpt et les premiers noeuds
"""
#Dans cette version, les data_ts sont obligatoire pour définir à l'avance les futurs breakpoints
class Tree_iSAX:

    """
    Fonction d'initialisation
    """
    def __init__(self,size_word,threshold,data_ts,base_cardinality=2):
        
        # nombre de lettre contenu dans le mot SAX
        self.size_word = size_word
        # seuil ou le noeud split
        self.threshold = threshold
        # cardinalité de chacune des lettres
        self.base_cardinality = base_cardinality
        
        # et on transmet tout cela au noeud root
        self.root = RootNode(self,[base_cardinality] * size_word)
        
        self.mu, self.sig = norm.fit(data_ts) # mean, var

        # bkpt fait appel à la classe NormalGaussian dans le fichier ../hotSAX/gaussian
        self.bkpt = NormalGaussian(self.mu, self.sig)

    """
    Fin fonction d'initialisation
    """


    """
    La fonction insert qui appel directement celle de son noeud root
    """
    def insert(self,new_timeserie):
        if len(new_timeserie) < self.size_word:
            print("Erreur !! "+new_timeserie+" est plus petit que size.word = "+self.size_word+". FIN")
        else:
            #if len(time_serie) % size_word != 0:
            #    print("Attention : len(time_serie) % size_word != 0:")
            #    print("La dernière lettre sera de taille ",len(time_serie) % size_word)
            self.root.insert(new_timeserie)


    """
    La fonction search doit trouver la série temp la plus similaire à celle indiquée en paramètre
    """
    def search(self,new_timeserie):
        if len(new_timeserie) < self.size_word:
            print("Erreur !! "+new_timeserie+" est plus petit que size.word = "+self.size_word+". FIN")
        else:
            return self.root.exactSearch(new_timeserie)


    # definit ici pour les tests...
    # TODO ne doit pas être accessible à l'utilisateur
    def mindist_PAA_iSAX(self, ts, s_isax):
        return self.root.mindist_PAA_iSAX(ts, s_isax)


    """
    La fonction exactSearch qui appelle son noeud root
    qui fait elle meme appelle à approximateSearch
    """
    def exactSearch(self,new_timeserie,knn=1):

        if knn == 1:
            return self.root.exactSearch(new_timeserie)
        else:
            return self.root.exactSearch_knn(new_timeserie,knn)


    # definit ici pour les tests...
    # TODO ne doit pas être accessible à l'utilisateur
    def approximateSearch(self,new_timeserie):
        return self.root.approximateSearch(new_timeserie)

