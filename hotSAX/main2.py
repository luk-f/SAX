import matplotlib.pyplot as plt
from scipy.integrate import quad
from numpy import mean as np_mean, var as np_var, linspace as np_linspace

from gaussian import gaussian
from sax import sax, pandas_sax, breakpoints

import matplotlib.dates as mdates
import pandas as pd

def test(data=None,precision_bp = 2000,nb_bp = 3,taille_fenetre = 10, breakp = None, abscisse = None):

    """Paramètres"""
    #donnees
    if data == None:
        data = [580.38,581.86,580.97,580.8,579.79,580.39,580.42,580.82,581.4,581.32,581.44,581.68,581.17,580.53,580.01,579.91,579.14,579.16,579.55,579.67,578.44,578.24,579.1,579.09,579.35,578.82,579.32,579.01,579,579.8,579.83,579.72,579.89,580.01,579.37,578.69,578.19,578.67,579.55,578.92,578.09,579.37,580.13,580.14,579.51,579.24,578.66,578.86,578.05,577.79,576.75,576.75,577.82,578.64,580.58,579.48,577.38,576.9,576.94,576.24,576.84,576.85,576.9,577.79,578.18,577.51,577.23,578.42,579.61,579.05,579.26,579.22,579.38,579.1,577.95,578.12,579.75,580.85,580.41,579.96,579.61,578.76,578.18,577.21,577.13,579.1,578.25,577.91,576.89,575.96,576.8,577.68,578.38,578.52,579.74,579.31,579.89,579.96,579.96,579.96]
    #valeur du découpage pour trouver les breakpoints
    #nombre de breakpoints > 0

    #Affichage variance et moyenne des données
    print("variance = ",np_var(data))
    print("ecart type = ",np_var(data)**0.5)
    print("moyenne = ",np_mean(data))

    #Calcul de l'intégrale de la gaussienne trouvé
    mu = np_mean(data)
    sig = np_var(data)
    ecart = (max(data)-min(data))
    integral_g = quad(gaussian, min(data)-ecart, max(data)+ecart, args=(mu,sig))
    print("integrale gauss",integral_g)
    print(mu,sig,ecart)
    
    #Appel de la fonctio SAX
    vector_c, vector_c_fit = sax(data,taille_fenetre)

def serie_to_sax(dataframe,serie_n,nb_bp = 3,taille_fenetre = 10, breakp = None, abscisse = None,precision_bp = 2000):

    if serie_n not in dataframe:
        raise ValueError("WARNING : ",serie_n," not in the DataFrame ->", dataframe.columns," !! Fin")
    
    fig = plt.figure(figsize=(15, 10))
    
    """Paramètres"""
    #valeur du découpage pour trouver les breakpoints
    #nombre de breakpoints > 0

    #Affichage variance et moyenne des données
    print("variance = ",dataframe[serie_n].var())
    print("ecart type = ",dataframe[serie_n].var()**0.5)
    print("moyenne = ",dataframe[serie_n].mean())

    #Calcul de l'intégrale de la gaussienne trouvé
    mu = dataframe[serie_n].mean()
    sig = dataframe[serie_n].var()
    ecart = (dataframe[serie_n].max()-dataframe[serie_n].min())
    integral_g = quad(gaussian, dataframe[serie_n].min()-ecart, dataframe[serie_n].max()+ecart, args=(mu,sig))
    print("integrale gauss",integral_g)
    print(mu,sig,ecart)
    
    #Appel de la fonctio SAX
    dataframe, vector_c_fit = pandas_sax(dataframe=dataframe,serie_n=serie_n,w=taille_fenetre)
    
    # plot des résultats
    if "Timestamp" in dataframe:
        plt.plot(dataframe['Timestamp'],dataframe[serie_n],c='r')
        plt.plot(dataframe['Timestamp'],dataframe['SAX'],c='b')
        
    plt.show()