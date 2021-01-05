def cleanVariableName(variableName: str) -> str:
    """
    Removes punctuation/spaces from variable names

    Args:
        variableName (str)

    Returns:
        str: without punctuation
    """

    fullName = ""

    for i, chunk in enumerate(variableName.split("!!")):
        newName = ""
        for subChunk in chunk.split(" "):
            newName += subChunk.capitalize().strip(r"(\s|:)")

        if i == 0:
            fullName += newName
        else:
            fullName += f"_{newName}"

    return fullName
