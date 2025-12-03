import pandas as pd
from typing import List, Optional, Sequence, Tuple, Any


def columns_list(
    df: Optional[pd.DataFrame],
    unwanted_el: Optional[Sequence[str]] = None,
    add_el: Optional[Sequence[Tuple[int, str]]] = None,
) -> List[str]:

    if df is None:
        return []

    cols = df.columns.tolist()

    if unwanted_el:
        cols = [c for c in cols if c not in unwanted_el]

    if add_el:
        for idx, name in add_el:
            idx = max(0, min(idx, len(cols)))
            cols.insert(idx, name)

    return cols

