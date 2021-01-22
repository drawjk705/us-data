def clean_variable_name(variable_name: str) -> str:
    """
    Removes punctuation/spaces from variable names

    Args:
        variable_name (str)

    Returns:
        str: without punctuation
    """

    full_name = ""

    for i, chunk in enumerate(variable_name.split("!!")):
        new_name = ""
        for sub_chunk in (
            chunk.replace(",", " ")
            .replace("-", " ")
            .replace(".", " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("/", " slash ")
            .split(" ")
        ):
            new_name += (
                sub_chunk.capitalize()
                .replace(" ", "")
                .replace(":", "")
                .replace("'", "")
            )

        if i == 0:
            full_name += new_name
        else:
            full_name += f"_{new_name}"

    return full_name
