import os


def save_contract(filename, content):

    os.makedirs("outputs", exist_ok=True)

    path = os.path.join("outputs", filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return path