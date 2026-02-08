import os
from pathlib import Path
from typing import List, Literal, cast

import pandas as pd
from google import genai 
from google.genai import types
from pydantic import BaseModel, Field
from IPython.display import display
import rich

class GenderItem(BaseModel):
    name: str = Field(..., description="Nome completo")
    gender: Literal["Masculino", "Feminino", "Unknown"]


class GenderClassification(BaseModel):
    results: List[GenderItem]


MUPE_METADATA_COLUMNS = [
    'split', 'braz_id', 'mupe_code', 'interviewee_name',
    'youtube_link', 'interviewer1', 'interviewer2', 'interviewer3', 'title',
    'gender', 'birth_state', 'interviewee_bio'
]

def preprocess_metadata_dataset(df:pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = cast(pd.DataFrame, df.loc[df['birth_country'] == 'Brasil'])
    df = cast(pd.DataFrame, df[MUPE_METADATA_COLUMNS])
    df = df.rename(columns={'braz_id': 'audio_id'})
    print(f"Number of rows with NA in 'audio_id': {df['audio_id'].isna().sum()}")
    df = df.dropna(subset=['audio_id'])
    df['audio_id'] = df['audio_id'].astype(int)
    return df


def get_gender_map(names: List[str]) -> GenderClassification | None:
    if not all(isinstance(n, str) and n.strip() for n in names):
        raise ValueError("All names must be non-empty strings")

    formatted_names = "\n".join(f"- {n.strip()}" for n in names)
    
    prompt = (
        "Classifique cada nome brasileiro listado abaixo como Masculino, Feminino ou Unknown. "
        'Responda somente com JSON no formato '
        '[{"name": "Nome", "gender": "Masculino|Feminino|Unknown"}, ...].\n\n'
        f"Nomes:\n{formatted_names}"
    )

    client = genai.Client(
        vertexai=True,
        api_key=os.environ.get("VERTEX_AI_API_KEY"),
    )

    config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        response_mime_type="application/json",
        response_schema=GenderClassification,
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            ],
            config=config,
        )

        assert isinstance((response_parsed := response.parsed), GenderClassification)

        return response_parsed
    except Exception as e:
        print(f"Error during Vertex AI execution: {e}")
        return None


if __name__ == "__main__":
    metadata_path = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/TESTE_DEV_TRAIN_mupe_metadados_289.xlsx - df_full6.csv")
    metadata_raw = pd.read_csv(metadata_path)
    display(metadata_raw.head())
    metadata_processed = preprocess_metadata_dataset(metadata_raw)
    mupe_metadata_sp = metadata_processed[metadata_processed['birth_state'].str.contains('Paulo')].reset_index(drop=True)
    names_mapped = get_gender_map(metadata_processed['interviewee_name'].tolist())
    rich.print(rich.inspect(names_mapped))