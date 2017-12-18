from scipy.integrate import quad
from numpy import inf as np_inf
from numpy import full
#import file from project
from numpy import arange, average
from numpy import shape as np_shape
from gaussian import gaussian

from pandas import Series

# Fonction SAX
# size_word représente le nombre de lettre contenu dans le mot SAX
def sax(time_serie,size_word,breakpoints):

    sax_word = []
    paa_word = ts_to_paa(time_serie, size_word)
    for paa_letter in paa_word:
        sax_word.append(paa_to_sax(paa_letter,breakpoints))

    return paa_word, sax_word

def paa_to_sax(value,breakpoints):
    sax = 0
    for var in breakpoints:
        if value < var:
            break
        sax += 1
    return sax

def preprocessing_ts_to_paa(time_serie,size_word):

    # on définit la taille des lettres, cad le nombre de points prit pour chaque lettre
    size_letter = int(len(time_serie) / size_word)
    # le pas de la fenetre de parcours de la serie sera égal à taillelettre
    step = size_letter
    # tous les points ont le même poids pour le calcul du paa
    weights = [1.0] * size_letter

    # maintenant on vérifie que le modulo
    modulo = len(time_serie) % size_word
    overtaking = 0

    # Si le modulo n'est pas nul, on réparti le point step+1
    if modulo != 0:
        # print("Attention : len(time_serie) % size_word != 0:")
        size_letter += 1
        overtaking = (len(time_serie) % size_word) / len(time_serie)
        weights.append(overtaking)

    len_time_serie = len(time_serie)
    return len_time_serie, modulo, step, weights, overtaking, size_letter

def loop_ts_to_paa(time_serie, len_time_serie, modulo, step, weights, overtaking, size_letter):

    #paa_word = full()
    paa_word = []
    for i in range(0, len_time_serie - modulo, step):
        start = i
        end = i + size_letter
        paa_letter = average(time_serie[start:end], weights=weights)
        paa_word.append(paa_letter)
        if overtaking != 0:
            weights[0] -= overtaking
            weights[-1] += overtaking

    return paa_word

def ts_to_paa(time_serie,size_word):
    len_time_serie, modulo, step, weights, overtaking, size_letter = preprocessing_ts_to_paa(time_serie, size_word)
    return loop_ts_to_paa(time_serie, len_time_serie, modulo, step, weights, overtaking, size_letter)

def list_ts_to_list_paa(list_time_serie,size_word):
    list_paa = []
    len_time_serie, modulo, step, weights, overtaking, size_letter = preprocessing_ts_to_paa(list_time_serie[0], size_word)
    for i in range(len(list_time_serie)):
        list_paa.append( loop_ts_to_paa(list_time_serie[i], len_time_serie, modulo, step, weights, overtaking, size_letter) )
    return list_paa

#Fonction SAX pour Serie Pandas
def pandas_sax(dataframe,serie_n,w):
    n = len(dataframe[serie_n])
    print("len c = ",n)
    
    serie_sax = []
    serie_sax_fit = Series()
    last = 0
    
    for i in range(0,n,w):
        start = i
        end = i + w
        mean_interval = dataframe[serie_n][start:end].mean()
        for z in range(start, end):
            serie_sax.append(mean_interval)
        last = i
        
    # TODO comme au dessus...
    for i in range(last+1,n):
        serie_sax.append(dataframe[serie_n][last+1:n])
        
    dataframe['SAX'] = Series(serie_sax)
        
    #print(dataframe['SAX'])

    return dataframe, serie_sax_fit

#On cherche les intervalles suivant la taille de l'alphabet
# Aire total de la gaussienne, min, mean, précision de découpage
def breakpoints(I, min, mean, prec, nb_bp, mu, sig):
    nb_bp_t = int(nb_bp/2)
    sol = []
    for inc in range(1,nb_bp_t+1):
        # TODO boucle très couteuse (taille du pas forcément..)... d'abord s'occuper du pourquoi toujours meme segment
        for i in arange(min, mean, (mean-min)/prec):
            #print(i)
            #print(quad(gaussian, -np.inf, i, args=(mu,sig))[0],">",I[0])
            # TODO coute cher de recalculer quad... d'abord s'occuper du TODO plus haut
            if quad(gaussian, -np_inf, i, args=(mu,sig))[0] > I[0]/(nb_bp+1)*inc:
                sol.append(i-(mean-min)/prec)
                break
    for it in range(len(sol),0,-1):
        sol.append(sol[it-1]+2*(mu-sol[it-1]))
    if nb_bp%2 != 0:
        sol.insert(int(len(sol)/2),mean)
    return sol


# Permet de retourner le bon nombre de bit suivant la cardinalité
# nous sert aussi pour la phase d'init de Tree_iSAX...
"""
def numberOfBit(cardinality):
    num = 1
    while cardinality / 2 != 1:
        num += 1
        cardinality /= 2
    return num
"""