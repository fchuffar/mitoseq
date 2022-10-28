def extract_haplogroups(filename: str) -> list:
    """
    Extract the haplogroups from a haplogrep result file and return a list of them and their ID.
    """
    result = []
    with open(filename, "r") as file:
        for line in file.readlines()[1:]:
            result.append(
                (line.split()[1].replace('"', ""), line.split()[0].replace('"', ""))
            )
    return result
