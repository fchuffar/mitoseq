import os


class Node:
    """_summary_"""

    def __init__(self):
        self.children = {}
        self.end_of_word = False
        self.occurence = 0
        self.full_text = ""

    def __repr__(self) -> str:
        return f"({self.full_text} {str(self.occurence)})"


class Trie:
    """_summary_"""

    def __init__(self):
        self.root = Node()
        self.stage = {}
        self.maxi = 0

    def insert(self, word: str, num: int, dictio: dict) -> None:
        """_summary_

        Args:
            word (str): _description_
            num (int): _description_
            dictio (dict): _description_
        """
        step = 0

        ptr = self.root
        temp = ""
        for count, letter in enumerate(word):
            temp += letter
            if temp not in ptr.children and word[: count + 1] in dictio:
                step += 1
                ptr.children[temp] = Node()
                ptr = ptr.children[temp]
                temp = ""
            elif temp in ptr.children:
                step += 1
                ptr = ptr.children[temp]
                temp = ""
        ptr.occurence = num
        ptr.end_of_word = True
        ptr.full_text = word
        if step not in self.stage:
            self.stage[step] = [ptr]
        else:
            self.stage[step].append(ptr)
        self.maxi = max(self.maxi, step)

    def search(self, word: str) -> tuple:
        """_summary_

        Args:
            word (str): _description_

        Returns:
            tuple: _description_
        """
        ptr = self.root
        temp = ""
        for count, letter in enumerate(word):
            temp += letter
            if temp not in ptr.children and count + len(temp) == len(word):
                return (False, 0)
            if temp not in ptr.children:
                pass
            else:
                ptr = ptr.children[temp]
                temp = ""
        if ptr.end_of_word:
            return (True, ptr.occurence)
        return (False, 0)

    def reorganize(self) -> None:
        """_summary_"""
        total = 0
        for i in range(self.maxi, 0, -1):
            for haplo in self.stage[i]:
                if haplo.children == {}:
                    pass
                else:
                    total += haplo.occurence
                    for num in haplo.children:
                        total += haplo.children[num].occurence
                    haplo.occurence = total
                    total = 0

    def find_haplo_match(self, word: str, min_num: int) -> str:
        """_summary_

        Args:
            haplogroup (str): _description_
            min_num (int): _description_

        Returns:
            str: _description_
        """
        ptr = self.root
        temp = ""
        best_fit = None
        for count, letter in enumerate(word):
            temp += letter
            if temp not in ptr.children and count + len(temp) == len(
                word
            ):  # a vérifier
                pass
            if temp not in ptr.children:
                pass
            else:
                ptr = ptr.children[temp]
                if ptr.occurence >= min_num:
                    best_fit = ptr
                temp = ""
        if ptr.end_of_word:
            try:
                return (best_fit.full_text, best_fit.occurence)
            except AttributeError:
                print(f"No haplogroup with enough count for {word}")
                return (False, 0)
        return (False, 0)


def extract_haplogroups(filename: str) -> list:
    """
    Extract the haplogroups from a haplogrep result file and return a list of them and their ID.
    """
    result = []
    file_list = []
    with open(file=f"data/output/{filename}", mode="r", encoding="utf-8") as file:
        for line in file.readlines()[1:]:
            result.append(line.split()[1].replace('"', ""))
            file_list.append(line.split()[5].replace('"', ""))
    return result, file_list


def create_dictio(filename: str) -> dict:
    """_summary_

    Args:
        filename (str): _description_

    Returns:
        dict: _description_
    """
    dictio = {}
    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines()[1:-4]:
            temp = line.split(",")
            dictio[temp[3]] = int(temp[5])
    return dictio


def prefix_tree(dictionary: dict) -> Trie:
    """_summary_

    Args:
        dictionary (dict): _description_

    Returns:
        Trie: _description_
    """
    the_tree = Trie()
    for key in dictionary:
        the_tree.insert(key, int(dictionary[key]), dictionary)
    return the_tree


def haplogroup_count(haplogroup_file: list, num, bank) -> list:
    """_summary_

    Args:
        haplogroups (list): _description_

    Returns:
        list: _description_
    """

    haplogroups, file_list = extract_haplogroups(haplogroup_file)
    dictio = create_dictio(bank)
    the_tree = prefix_tree(dictio)
    the_tree.reorganize()
    haplo_list = []
    for i, haplogroup in enumerate(haplogroups):
        test = the_tree.find_haplo_match(haplogroup, num)
        haplo_list.append((file_list[i], haplogroup, test[0], test[1]))
    return haplo_list


def fuse_haplogroups():
    with open("data/output/haplogroups.txt", "w", encoding="utf-8") as output_file:
        output_file.write(
            '"SampleID"	"Haplogroup"	"Rank"	"Quality"	"Range"	"Origin_Filename"\n'
        )
        for file in os.listdir("data/output/"):
            with open(f"data/output/{file}", encoding="utf-8") as input_file:
                for line in input_file.readlines()[1:]:
                    output_file.write(line.replace("\n", "") + f"  {file}\n")


def supp_esp(line_file):
    """Fonction qui supprime les espaces en début de ligne.
    Function that removes spaces at the beginning of a line."""
    if line_file.startswith(" "):  # Si la ligne commence par un espace
        line_file = line_file.strip()  # Suppression des espaces
    return line_file  # retourne la ligne sans les espaces en début de ligne


def clean_haplo_line(haplo_line):
    """Fonction qui prend la line de l'haplogroupe et rend uniquement l'haplogroupe.
    Function that takes the haplogroup row and returns only the haplogroup."""
    split_line = haplo_line.split()  # sépare la ligne selon les espaces
    haplogroup = split_line[1].split('"')  # sépare la ligne selon les guillemets
    return haplogroup[1]


def clean_access_line(access_line):
    """Fonction qui prend la ligne de l'accession et rend uniquement l'accession.
    Function that takes the accession row and returns only the accession."""
    split_line = access_line.split()
    data = split_line[1].split('"')
    accession = data[1]
    return accession


def parser(phylotree_file):
    """Fonction qui lit le fichier phylotree et retroune les lignes correspondants aux haplogroupes et
    celle correspondant aux accessions dans une liste de tuples (haplogroupe;accession).

    Function that reads the phylotree file and returns rows corresponding to haplogroups and
    the one corresponding to the accessions in a list of tuples (haplogroup;accession)."""

    list_haplogroup = []  # Création d'une liste de stockage des lignes 'haplogroupes'
    list_accession = []  # Création d'un liste de stokage des lignes 'accession'
    bool = False  # Booléen pour vérification que chaque accession a été prise après un haplogroupe
    with open(
        phylotree_file, "r"
    ) as phylo_data:  # On parcours le fichier 'phylotree' donné en entrée

        for line in phylo_data:  # Pour chaque ligne...
            line = supp_esp(line)  # Appel de la fonction qui supprime les espaces

            if line.startswith(
                "<haplogroup name="
            ):  # Si la ligne correspond a l'haplogroupe
                haplogroup = clean_haplo_line(
                    line
                )  # Appel de la fonction qui 'clean' la ligne
                list_haplogroup.append(
                    haplogroup
                )  # on ajoute a la liste de stokage correspondante
                bool = True
            elif (
                line.startswith("<details accessionNr=") and bool == True
            ):  # Si la ligne correspond a l'accession et que la ligne d'avant était un haplogroupe
                accession = clean_access_line(
                    line
                )  # Appel de la fonction qui 'clean' la ligne
                list_accession.append(
                    accession
                )  # on ajoute a la liste de stokage correspondante
                bool = False

    """
    print(len(list_accession))      #Vérification que le nombre d'accession et le nombre d'haplogroup sont égaux
    print(len(list_haplogroup))
    """

    tuple_haplogroup_accession = list(zip(list_haplogroup, list_accession))
    """
    with open ('haplogroup_file', 'w') as file :    #creation de fichier contenant les listes (aide à la visualisation)
        file.write(f'{list_haplogroup}')
    with open ('accesion_file', 'w') as file : 
        file.write(f'{list_accession}')
    with open ('haplo_access_file', 'w') as file : 
        file.write(f'{tuple_haplogroup_accession}')
    """

    return tuple_haplogroup_accession  # retourne les listes de stockages


def haplogroupe_accession(phylotree_file, haplogroupe):
    """Fonction qui donne l'accession depuis un haplogroupe donné.
    Function that gives accession from a given haplogroup."""
    tuple_haplo_access = parser(phylotree_file)  # Appel de la fonction parser

    accession = ""
    for i in range(
        (len(tuple_haplo_access) - 1)
    ):  # '-1' car dans python position 1 = 0 donc position n = n-1

        if str(tuple_haplo_access[i][0]) == str(
            haplogroupe
        ):  # Si l'haplogroupe donné est le même que l'un provenant de la liste de tuple, On s'interesse a l'accession
            if (
                str(tuple_haplo_access[i][1]) == ""
            ):  # S'il n'y en pas alors elle est égal a None
                accession = None
            else:
                accession = tuple_haplo_access[i][
                    1
                ]  # Sinon elle prend la valeur de l'accession du tuple
        else:
            continue
    return accession
