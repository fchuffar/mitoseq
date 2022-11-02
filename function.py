import argparse
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
            if temp not in ptr.children and count + len(temp) == len(word):
                return (False, 0)
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
    with open(file=f"Data/Output/{filename}", mode="r", encoding="utf-8") as file:
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
    with open("Data/Output/haplogroups.txt", "w", encoding="utf-8") as output_file:
        output_file.write(
            '"SampleID"	"Haplogroup"	"Rank"	"Quality"	"Range"	"Origin_Filename"\n'
        )
        for file in os.listdir("Data/Output/"):
            with open(f"Data/Output/{file}", encoding="utf-8") as input_file:
                for line in input_file.readlines()[1:]:
                    output_file.write(line.replace("\n", "") + f"  {file}\n")
