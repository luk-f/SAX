from anytree import Node
from numpy import amax, argmin, sqrt, std, full, inf
from numpy import mean as np_mean
from scipy.spatial.distance import euclidean as d_eucli
from copy import deepcopy
from queue import PriorityQueue as pqueue

from bsf import BestSoFarList

from sys import path
path.insert(0, './hotSAX')
from sax import ts_to_paa, paa_to_sax, list_ts_to_list_paa
path.insert(0, '../')

class RootNode(Node):

    # TODO attribut global rajouté pour les tests
    cmpt_seg_split = []

    """
    Debut de la fonction d'initialisation
    """
    def __init__(self, arbre, cardinality_next):

        Node.__init__(self, "root")
        print("create -> root")

        self.arbre = arbre
        self.cardinality_next = cardinality_next

        self.nodes = {}

    """
    Fin de la fonction d'initialisation
    """

    """
    ATTENTION, comparaison entre noeud ici aucun interet
    Par contre on pourrait donner un ordre de prio suivant cardinalité ou encore objets sous le noeud
    Seulement redefini pour PriorityQueue
    Car si ils sont à la même distance lors de queue.put((dist,noeud)), il va utiliser cet opérateur pour comparer les noeuds entre eux
    """
    def __lt__(self, y):
        return True

    """
    La fonction Insert(ts)
    """
    def insert(self, new_timeserie):

        # print("----------")
        # print("Appel de la fct insert du noeud ",self.name," pour la serie ",new_timeserie)

        # Normalement, comme nous sommes dans un Tree, on devrait:
        # - déjà avoir nos breakpoints
        # - et donc chercher si nos noeuds existent

        # C'est ici que commence la fonction d'origine et générique
        iSAX_word = self.iSAX_next(new_timeserie)
        # print("   iSAX de la serie : ",iSAX_word)
        # print("    dans le noeud ",self)


        # pour isax_word, on retourne le premier element de chaque tuple
        if str([i[0] for i in iSAX_word]) in self.nodes:
            # print("   okay idem!")
            current_node = self.nodes[str([i[0] for i in iSAX_word])]
            # print("   comp ",current_node.sax," and ",iSAX_word)

            # Si c'est une feuille
            if current_node.terminal:
                # et que l'on ne dépasse pas le seuil max
                if (current_node.nb_timeseries) < self.arbre.threshold:
                    current_node.insert(new_timeserie)
                # et que l'on dépasse le seuil max
                else:
                    # print("   Noeud ",str(current_node.sax)," déborde! nb ts :",current_node.nb_timeseries)
                    new_node = InternalNode(self.arbre, current_node.parent, deepcopy(current_node.sax),
                                            deepcopy(current_node.cardinality),current_node.timeseries)
                    # print("   breakpt: ",self.arbre.breakpoints)
                    new_node.insert(new_timeserie)
                    for ts in current_node.timeseries:
                        new_node.insert(ts)
                    del self.nodes[str(current_node.sax)]
                    self.nodes[str(current_node.sax)] = new_node
                    current_node.parent = None
                    del current_node

            # Sinon si ce n'est pas une feuille, on continue le parcours
            else:
                # print("   ce nest pas une feuille, on continue...")
                current_node.insert(new_timeserie)

        # Si on a rien trouvé
        else:

            # print("   rien trouvé, on crée un nouveau noeud")
            new_node = TerminalNode(self.arbre, self, [i[0] for i in iSAX_word], self.cardinality_next)
            new_node.insert(new_timeserie)
            self.nodes[str([i[0] for i in iSAX_word])] = new_node

    def iSAX_next(self, new_timeserie):

        paa_word = ts_to_paa(new_timeserie, self.arbre.size_word)
        iSAX_word = []

        for i in range(len(paa_word)):
            current_card = self.cardinality_next[i]
            iSAX_letter = -1
            current_breakpoints = self.arbre.bkpt.getBreakpointsByCardinality(current_card)
            iSAX_letter = paa_to_sax(paa_word[i],current_breakpoints)
            iSAX_word.append([iSAX_letter, current_card])
        return iSAX_word

    """
    Fonction permettant de calculer le mindist entre une série temporelle ts et un mot isax
    ts sera converti en mot paa (et aura donc la même longueur que le mot isax)
    """

    def mindist_PAA_iSAX(self, ts, s_isax):
        result = 0
        t_paa = ts_to_paa(ts, self.arbre.size_word)

        # pour pas s'embrouiller...
        # s_isax contient un mot iSAX !!!
        s_sax = [i[0] for i in s_isax]
        s_card = [i[1] for i in s_isax]

        if len(t_paa) == len(s_sax):
            n = len(ts)
            w = len(t_paa)

            # print("n : ",n,"  et w : ",w)

            for i in range(len(s_sax)):
                b_Li = float("-inf")
                b_Ui = float("inf")
                list_brkpt = sorted(self.arbre.bkpt.getBreakpointsByCardinality(s_card[i]))
                # print(b_Li,b_Ui)
                if s_sax[i] > 0:
                    b_Li = list_brkpt[s_sax[i] - 1]
                    # print("modif brpt L ",b_Li)
                """
                TODO : modifier par list_breakpoints
                """
                if s_sax[i] < len(list_brkpt):
                    b_Ui = list_brkpt[s_sax[i]]
                    # print("modif brpt U ",b_Ui)

                if t_paa[i] < b_Li:
                    # print("Pour <",i," diff = ",(b_Li - t_paa[i]))
                    result += (b_Li - t_paa[i]) * (b_Li - t_paa[i])
                elif t_paa[i] > b_Ui:
                    # print("Pour >",i," diff = ",(b_Ui - t_paa[i])," avec bkpt = ",b_Ui," et t_paa = ",t_paa[i])
                    result += (b_Ui - t_paa[i]) * (b_Ui - t_paa[i])
            result = sqrt(result)
            result *= sqrt(n / w)
            # print(result)
            return result
        else:
            print("mindist_PAA_iSAX : erreur len(t_paa) == len(s_isax) !");
            return -1

    """
    La fonction exactSearch qui fait elle meme appelle à approximateSearch
    """
    def exactSearch(self, new_timeserie):

        bestsofar_index = self.approximateSearch(new_timeserie)
        #print("result approximate :",bestsofar_index.iSAX_word)
        #print("result approximate :",bestsofar_index.timeseries,"\n")
        bestsofar_dist, _ = self.indexFileDist(new_timeserie, bestsofar_index)

        pq = pqueue()
        pq.put((0, self))

        while not pq.empty():
            min = pq.get()
            if min[0] >= bestsofar_dist:
                break
            if min[1].is_leaf:
                tmp, _ = self.indexFileDist(new_timeserie, min[1])
                if bestsofar_dist > tmp:
                    bestsofar_dist = tmp
                    bestsofar_index = min[1]
            # dans l'algo d'origine c'est un elif internal ou root
            else:
                for sax, child_node in min[1].nodes.items():
                    node_dist = self.mindist_PAA_iSAX(new_timeserie,child_node.iSAX_word)
                    pq.put((node_dist, child_node))
                    #print("CA MARCHE !!")

        return bestsofar_index
    

    """
    La fonction exactSearch_knn qui fait elle meme appelle à approximateSearch
    Recherche les knn
    """
    # TODO attention il faut adapter approximateSearch pour que bsf_list soit de suite full!
    # TODO car ici on risque d'ajouter beaucoup trop de noeud inutile tant que bsf_list is not full...
    def exactSearch_knn(self, new_timeserie, knn=1):

        bestsofar_index = self.approximateSearch(new_timeserie)
        bestsofar_dist, st_min = self.indexFileDist(new_timeserie, bestsofar_index)

        bsf_list = BestSoFarList(knn)
        bsf_list.addElement(bestsofar_dist, bestsofar_index, st_min)

        pq = pqueue()
        pq.put((0, self))

        while not pq.empty():
            min = pq.get()
            if min[0] >= bsf_list.dist and bsf_list.isFull():
                break
            if min[1].is_leaf:
                for elem in min[1].timeseries:
                    if bsf_list.dist > d_eucli(new_timeserie, elem) or not bsf_list.isFull():
                        bsf_list.addElement(d_eucli(new_timeserie, elem), min[1], elem)
            # dans l'algo d'origine c'est un elif internal ou root
            else:
                for sax, child_node in min[1].nodes.items():
                    node_dist = self.mindist_PAA_iSAX(new_timeserie,child_node.iSAX_word)
                    pq.put((node_dist, child_node))
                    #print("CA MARCHE !!")

        return bsf_list.list


    """
    La fonction approximateSearch
    """
    def approximateSearch(self, new_timeserie):
        #print("self.cardinality_next ", self.cardinality_next)
        n_ts_isax = self.iSAX_next(new_timeserie)
        #print("conversion ", n_ts_isax)
        # print(self.nodes)

        if str([i[0] for i in n_ts_isax]) in self.nodes:
            # print("jinvoque mon fils préféré")
            return self.nodes[str([i[0] for i in n_ts_isax])].approximateSearch(new_timeserie)
        ##
        ## TODO pourquoi ne pas prendre le fils ayant le plus petit mindist?
        ## Trop couteux???
        else:
            # print("jinvoque mon fils ainé pour ", self.iSAX_word)
            first = next(iter(self.nodes))
            #print(self.nodes[first].iSAX_word)
            return self.nodes[first].approximateSearch(new_timeserie)


    def indexFileDist(self, ts, node):

        dist_min = float('inf')
        st_min = None
        for ts_node in node.timeseries:
            diff = d_eucli(ts,ts_node)
            if diff < dist_min:
                dist_min = diff
                st_min = ts_node

        #print("fin indexfildist = ",dist_min)
        return dist_min, st_min


    def indexFileDist_ListTS(self, ts, list_ts):

        dist_min = float('inf')
        st_min = None
        for ts_node in list_ts:
            diff = d_eucli(ts,ts_node)
            if diff < dist_min:
                dist_min = diff
                st_min = ts_node

        #print("fin indexfildist = ",dist_min)
        return dist_min, st_min


###
### TODO faire une class abstraite ClassicNode pour faire un init en commun
### pour internal et terminal
###
### et on peut utiliser la classe NodeMixin potentiellement pour afficher des infos dans l'arbre Node natif
###


class InternalNode(RootNode):

    """
    def split(self,list_ts_paa,ratio_next_cardinality=2):

        # print("ratio_next_cardinality = ",ratio_next_cardinality)
        # NB : dans l'article, soit disant pas de coût supplémentaire...
        # Veulent-ils que l'on conserve le paa de la série AVEC la série (dans ce cas créer un objet série)
        mean, stdev = self.computeMeanStDev(list_ts_paa)
        #print("stdev ", stdev)
        segmentToSplit = None
        segToSpli_dist = float('inf')
        # print(len(list_ts_paa[0]))
        # TODO Comme la boucle est aussi faite dans computeMeanStdev, pourquoi pas mutualiser?
        for i in range(len(list_ts_paa[0])):
            #print("-",i)
            #print("segment num ",i," avec self.cardinality[i]*ratio_next_cardinality = ",self.cardinality[i]*ratio_next_cardinality)
            b = self.arbre.bkpt.getOnlyLastBreakpointsByCardinality(self.cardinality[i]*ratio_next_cardinality)
            bkptNN = float('inf')
            dist_bkpt = float('inf')
            for j in range(len(b)):
                #print("breakpoint num ",j)


                if abs(mean[i]-b[j]) < bkptNN:
                    bkptNN = abs(mean[i]-b[j])

                # TEST mesure dist entre bkpt
                if j < len(b)-1:
                    for k in range(j+1,len(b)):
                        if abs(b[k] - b[j]) < dist_bkpt:
                            dist_bkpt = abs(b[k] - b[j])

                # FIN TEST mesure dist entre bkpt


                if mean[i] - stdev[i]*3 <= b[j] and b[j] <= mean[i] + stdev[i]*3:
                    #print("okay inclu pour ", i, (abs( (b[j] - mean[i])/stdev[i] ) ) )
                    if (abs( (b[j] - mean[i])/stdev[i] ) ) < segToSpli_dist :
                        segmentToSplit = i
                        segToSpli_dist = abs(b[j] - mean[i])

            #print(bkptNN, len(b))
            #print(dist_bkpt)
            #print(bkptNN/dist_bkpt,len(b))
        """

    def split(self, list_ts_paa, next_cardinality, mean, stdev):

        # NB : dans l'article, soit disant pas de coût supplémentaire...
        # Veulent-ils que l'on conserve le paa de la série AVEC la série (dans ce cas créer un objet série)

        segmentToSplit = None
        segToSpli_dist = float('inf')
        # C'est le(s) memes breakpoints pour tout les segments candidats
        # Comme ça pas de jaloux !
        b = self.arbre.bkpt.getOnlyLastBreakpointsByCardinality(next_cardinality)
        # TODO Comme la boucle est aussi faite dans computeMeanStdev, pourquoi pas mutualiser?
        for i in range(len(list_ts_paa[0])):
            # TODO faire une fonction qui retourne rapidement les plus proches...?
            # ici breakpoint le plus proche
            bNN = min(b, key=lambda x:abs(x-mean[i]))
            # anciennement : for j in range(len(b)):
            # si la cardilalité du segment i est plus petit que la prochaine cardinalité envisagée
            if self.cardinality[i] < next_cardinality:
                # Ici si : mean[i] - stdev[i] * 3 <= b[j] <= mean[i] + stdev[i] * 3
                if abs(bNN - mean[i]) <= stdev[i] * 3:
                    if (abs((bNN - mean[i]) / stdev[i])) < segToSpli_dist:
                        segmentToSplit = i
                        segToSpli_dist = abs(bNN - mean[i])

        ### attention, si aucun candidat, alors rappeler la fonction avec une cardinalité plus haute
        if segmentToSplit is None:
            segmentToSplit, next_cardinality = self.split(list_ts_paa, next_cardinality=(next_cardinality*2), mean=mean, stdev=stdev)
        return segmentToSplit, next_cardinality

    def __init__(self, arbre, parent, sax, cardinality, timeseries):

        self.iSAX_word = []
        for i in range(len(sax)):
            self.iSAX_word.append([sax[i], cardinality[i]])

        Node.__init__(self, parent=parent, name=str(self.iSAX_word))

        self.arbre = arbre
        self.sax = sax
        self.cardinality = cardinality

        # TODO attention si split est appelé recursivement, ne retourne pas le card nécessaire
        # TODO donc sera forcément rappelé, est donc un noeud intermédiaire qui ne sert à rien
        list_ts_paa = list_ts_to_list_paa(timeseries, self.arbre.size_word)
        # TODO pourquoi toujours meme segment
        mean, stdev = self.computeMeanStDev(list_ts_paa)
        position_min, next_cardinality = self.split(list_ts_paa, min(self.cardinality), mean, stdev)
        # TODO attribut global rajouté pour les tests
        self.cmpt_seg_split.append(position_min)
        self.cardinality_next = deepcopy(self.cardinality)
        # TODO : réfléchir si c'est une bonne idée...
        # TODO self.cardinality_next[position_min] = next_cardinality
        self.cardinality_next[position_min] *= 2

        # Spécifique aux noeuds internes
        self.nodes = {}

        self.terminal = False

    def __str__(self):

        str_print = "InternalNode\n\tiSAX : " + self.name + "\n\tparent iSAX : " + self.parent.name + "\n\tcardinalité : "
        str_print += str(self.cardinality) + "\n\tcardinalité suiv : " + str(self.cardinality_next) + "\n\tnbr noeud fils : "
        str_print += str(len(self.nodes))

        return str_print

    def getTimeseries(self):
        timeseries = []
        for key, _ in self.nodes.items():
            for ts in self.nodes[key].getTimeseries():
                timeseries.append(ts)
        return timeseries

    def computeMeanStDev(self,list_ts_paa):

        mean = full(len(list_ts_paa[0]), inf)
        stdev = full(len(list_ts_paa[0]), inf)
        for i in range(len(list_ts_paa[0])):
            seg_i = [ts[i] for ts in list_ts_paa]
            mean[i] = np_mean(seg_i)
            stdev[i] = std(seg_i)
        return mean, stdev


class TerminalNode(RootNode):

    def __init__(self, arbre, parent, sax, cardinality):
        self.iSAX_word = []
        for i in range(len(sax)):
            self.iSAX_word.append([sax[i], cardinality[i]])

        Node.__init__(self, parent=parent, name=str(self.iSAX_word))
        # print("  -create -> terminal",str(iSAX_word))

        self.arbre = arbre
        self.sax = sax
        self.cardinality = cardinality
        self.cardinality_next = None

        # Spécifique aux noeuds terminaux
        # (quoi? on dit des noeuds terminals?)

        # Nombre de series temportelles contenu dans le noeud (ou par ses fils)
        self.nb_timeseries = 0
        # Si c'est une feuille, contient une liste de séries temporelles, sinon contient liste vide
        self.timeseries = []
        # TODO si seuil connu, pourquoi pas un narray numpy...

        self.terminal = True

    def insert(self, ts):
        self.timeseries.append(ts)
        self.nb_timeseries += 1

    def __str__(self):
        str_print = "TerminalNode\n\tiSAX : " + self.name + "\n\tparent iSAX : " + self.parent.name + "\n\tcardinalité : "
        str_print += str(self.cardinality) + "\n\tcardinalité suiv : " + str(self.cardinality_next) + "\n\tnbr timeseries : "
        str_print += str(self.nb_timeseries)

        return str_print

    def approximateSearch(self, new_timeserie):
        return self

    def getTimeseries(self):
        return self.timeseries
