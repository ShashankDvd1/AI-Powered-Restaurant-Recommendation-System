"""Load Zomato dataset from Hugging Face."""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


def load_raw_dataframe() -> pd.DataFrame:
    """
    Load the Hugging Face dataset and return a pandas DataFrame.

    Handles single or multi-split datasets (uses ``train`` split when present).
    """
    dataset = load_dataset(DATASET_ID)
    if hasattr(dataset, "keys") and "train" in dataset.keys():
        table = dataset["train"]
    else:
        # Single split or DatasetDict with one key
        split_name = next(iter(dataset.keys()))
        table = dataset[split_name]

    df = table.to_pandas()
    # Normalize column names for mapping
    df.columns = [str(c).strip() for c in df.columns]
    return df
