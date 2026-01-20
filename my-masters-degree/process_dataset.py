import re
import os
import difflib
from pathlib import Path
from typing import List, Tuple, cast

import rich
import datasets
import numpy as np
import pandas as pd
from google import genai 
from google.genai import types
from datasets import Audio
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field


class QuestionMetadata(BaseModel):
    id: int = Field(..., description="O ID numérico da pergunta (ex: 0, 2, 4)")
    timestamp: str = Field(..., description="O timestamp original (ex: 00:06)")

class SubSection(BaseModel):
    subtitle: str = Field(..., description="O subtítulo do roteiro (ex: IDENTIFICAÇÃO)")
    items: List[QuestionMetadata]

class Section(BaseModel):
    title: str = Field(..., description="O título principal do roteiro (ex: INTRODUÇÃO)")
    subsections: List[SubSection]

class InterviewSegmentation(BaseModel):
    segments: List[Section]


def split_interview_questions(questions:str) -> InterviewSegmentation | None:
    
    #TODO should move the content locally?
    with open("./roteiro_entrevista.md", "r") as f:
        roteiro_entrevista_md = f.read()

    prompt = f"""
    Você é um especialista em história oral e análise de transcrições. 
    Sua tarefa é segmentar a transcrição de uma entrevista fornecida abaixo de acordo com o Roteiro de Perguntas oficial.

    REGRAS DE PROCESSAMENTO:
    1. Analise o conteúdo semântico de cada linha da transcrição para decidir a qual seção/subseção do roteiro ela pertence.
    2. Se um tema fugir do roteiro (ex: falar de faculdade na seção errada), aloque-o na seção semanticamente mais próxima (ex: faculdade -> Escola/Formação).
    3. **CRUCIAL**: Na saída, NÃO inclua o texto da pergunta. Retorne APENAS o 'id' e o 'timestamp' dentro da estrutura hierárquica correta.
    4. Mantenha a ordem cronológica original das perguntas dentro dos grupos.

    ROTEIRO BASE:
    {roteiro_entrevista_md}

    TRANSCRIÇÃO PARA SEGMENTAR:
    {questions}
    """

    client = genai.Client(
        vertexai=True,
        api_key=os.environ.get("VERTEX_AI_API_KEY"),
    )

    model = "gemini-3-pro-preview"
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        
        response_mime_type="application/json",
        response_schema=InterviewSegmentation,

        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            ],
            config=generate_content_config,
        )
        
        assert isinstance((response_parsed := response.parsed), InterviewSegmentation)
        return response_parsed
    except Exception as e:
        print(f"Erro na execução do Vertex AI: {e}")
        return None
    

def aggregate_sample_dialogues(mupe_df: pd.DataFrame, audio_id: int) -> tuple[pd.DataFrame, list[int]]:
    """
    Aggregate contiguous utterances for a given audio_id and detect missing file counters.

    Returns
    -------
    tuple[pd.DataFrame, list[int]]
        - Aggregated blocks with merged interviewer turns.
        - Sorted list of missing file_id counters.
    """
    sample = mupe_df.loc[mupe_df["audio_id"] == audio_id].sort_values("start_time").copy()
    if sample.empty:
        raise ValueError(f"No rows found for audio_id={audio_id}")

    speaker_counts = sample["speaker_code"].value_counts()
    if len(speaker_counts) > 1:
        interviewer_codes = speaker_counts.index[1:]
        join_code = "_".join(interviewer_codes)
        sample.loc[sample["speaker_code"].isin(interviewer_codes), "speaker_code"] = join_code

    block_id = (sample["speaker_code"] != sample["speaker_code"].shift()).cumsum()
    file_id_series = sample["file_path"].str.extract(r"pc_ma_hv064_(?P<file_id>\d+)_")["file_id"].astype(int)

    df_agg = (
        sample.assign(block_id=block_id, file_id=file_id_series)
        .groupby("block_id")
        .agg(
            file_path=("file_path", list),
            file_id=("file_id", list),
            speaker_code=("speaker_code", "first"),
            start_time=("start_time", "min"),
            end_time=("end_time", "max"),
            duration=("duration", "sum"),
            original_text=("original_text", " ".join),
        )
        .reset_index(drop=True)
    )

    if file_id_series.empty:
        return df_agg, []

    file_ids = file_id_series.to_numpy(dtype=int)
    expected = set(range(file_ids.min(), file_ids.max() + 1))
    missing_ids = sorted(expected.difference(file_ids))
    return df_agg, missing_ids