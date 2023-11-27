import csv


def str_to_int(s: str) -> int | str:
    """
    returns an integer from a numeric string
    """
    try:
        converted = int(s)
    except ValueError:
        converted = s
    return converted


def str_to_float(s: str) -> float | str:
    """
    returns a float value from a numeric string
    if the input cannot be converted, keep the original string

    """
    try:
        converted = float(s)
    except ValueError:
        converted = s
    return converted


def read_csv_file(filename: str) -> list[list[str]]:
    """
    Returns a list of list of strings representing the text data in the file at
    'filename'
    """

    csv_acc = []  # File data goes here
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            csv_acc.append(line)
    return csv_acc
