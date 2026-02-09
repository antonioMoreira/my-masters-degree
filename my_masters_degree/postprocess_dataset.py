import ast
from typing import List

import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


def parse_list_str(v: str | List) -> List:
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return []
    return []


class MupeTalkSchema(pa.DataFrameModel):
    file_path: Series[List[str]]
    file_id: Series[List[int]]
    speaker_code: Series[str]
    start_time: Series[float]
    end_time: Series[float]
    duration: Series[float]
    original_text: Series[str]
    subsection: Series[str]
    group_id: Series[int]


def load_and_validate_mupetalk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Convert stringified lists to actual lists
    df["file_path"] = df["file_path"].apply(parse_list_str)
    df["file_id"] = df["file_id"].apply(parse_list_str)
    
    # Validate schema
    return MupeTalkSchema.validate(df)


def get_statistics(mupetalk_df: pd.DataFrame):
    pass
    

if __name__ == "__main__":
    df = pd.read_csv("/home/antonio-moreira/Documents/my-masters-degree/notebooks/mupetalk_train.csv")
    validated_df = load_and_validate_mupetalk(df)
    get_statistics(validated_df)