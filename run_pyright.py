import os
from typing import Any, Dict, List, cast

import toml


def run_pyright() -> None:
    """
    Automatically run pyright on all dependencies
    """

    tomlDict: Dict[str, Any] = {}

    with open("pyproject.toml", "r") as f:
        tomlDict = cast(Dict[str, Any], toml.load(f))

    dependencies = cast(
        List[str],
        [
            dep
            for dep in tomlDict["tool"]["poetry"]["dependencies"].keys()
            if dep != "python"
        ],
    )

    cmd = f"pyright . --createstub {' '.join(dependencies)}"

    print(cmd)

    os.system(cmd)


if __name__ == "__main__":
    run_pyright()
