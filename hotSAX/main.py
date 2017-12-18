import matplotlib.pyplot as plt
from scipy.integrate import quad
from numpy import mean as np_mean, var as np_var, linspace as np_linspace

from gaussian import gaussian
from sax import sax, breakpoints

import matplotlib.dates as mdates

def test(data=None,precision_bp = 2000,nb_bp = 3,taille_fenetre = 10, breakp = None, abscisse = None):

    """Paramètres"""
    #donnees
    if data == None:
        data = [580.38,581.86,580.97,580.8,579.79,580.39,580.42,580.82,581.4,581.32,581.44,581.68,581.17,580.53,580.01,579.91,579.14,579.16,579.55,579.67,578.44,578.24,579.1,579.09,579.35,578.82,579.32,579.01,579,579.8,579.83,579.72,579.89,580.01,579.37,578.69,578.19,578.67,579.55,578.92,578.09,579.37,580.13,580.14,579.51,579.24,578.66,578.86,578.05,577.79,576.75,576.75,577.82,578.64,580.58,579.48,577.38,576.9,576.94,576.24,576.84,576.85,576.9,577.79,578.18,577.51,577.23,578.42,579.61,579.05,579.26,579.22,579.38,579.1,577.95,578.12,579.75,580.85,580.41,579.96,579.61,578.76,578.18,577.21,577.13,579.1,578.25,577.91,576.89,575.96,576.8,577.68,578.38,578.52,579.74,579.31,579.89,579.96,579.96,579.96]
    #valeur du découpage pour trouver les breakpoints
    #nombre de breakpoints > 0
    
    fig = plt.figure(figsize=(15, 10))
    
    # TODO arranger les axes ici !!!
    years = mdates.YearLocator()
    yearsFmt = mdates.DateFormatter('%Y')
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    daysFmt = mdates.DateFormatter('%d')
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator()
    
    gauss = fig.add_subplot(2,1,1)
    gauss.xaxis.set_major_locator(daysFmt)
    gauss.xaxis.set_minor_locator(hours)
    #plt.ylabel('some numbers')

    #Affichage variance et moyenne des données
    print("variance = ",np_var(data))
    print("ecart type = ",np_var(data)**0.5)
    print("moyenne = ",np_mean(data))

    #Calcul de l'intégrale de la gaussienne trouvé
    mu = np_mean(data)
    sig = np_var(data)
    ecart = (np.amax(data)-np.amin(data))
    integral_g = quad(gaussian, np.amin(data)-ecart, np.amax(data)+ecart, args=(mu,sig))
    print("integrale gauss",integral_g)

    #Appel de la fonctio SAX
    vector_c, vector_c_fit = sax(data,taille_fenetre)
    if abscisse is None:
        plt.plot(vector_c)
        plt.plot(data)
    else:
        plt.plot(abscisse,vector_c)
        plt.plot(abscisse,data)

    if breakp is None:
        breakp = breakpoints(integral_g, min(data), np_mean(data), precision_bp, nb_bp, mu, sig)
    for bp in breakp:
        print("seuil : ",bp)
        plt.axhline(bp,c='grey')
        #print("seuil 2 : ",bp+2*(mu-bp))
        #plt.axhline(bp+2*(mu-bp))
        

    #Affichage de la gaussienne
    #fig.add_subplot(2,1,2)
    """
    x = np_linspace(min(data)-ecart,max(data)+ecart,100)
    plt.plot(x,gaussian(x,mu,sig))
    for bp in breakp:
        plt.axvline(bp)
    fig.add_subplot(2,1,1)
    """

    tab_classif= [0] * (len(breakp)+1)
    print(tab_classif)

    """
    for val in vector_c:
        it = 0
        for var in breakp:
            if val < var:
                tab_classif[it] = tab_classif[it] + 1
                break
            it = it + 1
    """
    
    pos_x = 1
    for val in vector_c_fit:
        it = 0
        test = 0
        int_char = 0
        for var in breakp:
            if val < var:
                tab_classif[it] = tab_classif[it] + 1
                test = 1
                # conversion en binaire str(bin(int_char))[2:]
                plt.annotate(str(bin(int_char))[2:], xy=(taille_fenetre * pos_x - taille_fenetre/2, val), xytext=(taille_fenetre * pos_x - taille_fenetre/2, val + 2),
                             arrowprops=dict(facecolor='white', shrink=0.05),
                             )
                break
            it = it + 1
            int_char = int_char + 1
        if test == 0:
            tab_classif[it] = tab_classif[it] + 1
            # conversion en binaire str(bin(int_char))[2:]
            plt.annotate(str(bin(int_char))[2:], xy=(taille_fenetre * pos_x - taille_fenetre/2, val), xytext=(taille_fenetre * pos_x - taille_fenetre/2, val + 2),
                         arrowprops=dict(facecolor='white', shrink=0.05),
                         )
        pos_x = pos_x + 1
    
    print(tab_classif)

    plt.show()
    return breakp   