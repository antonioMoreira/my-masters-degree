import os
from enum import Enum
from typing import List

import rich
import pandas as pd
from google import genai 
from google.genai import types
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


class ClassLabel(str, Enum):
    INTRODUCAO = "INTRODUÇÃO"
    IDENTIFICACAO = "IDENTIFICAÇÃO"
    INFANCIA = "INFÂNCIA"
    FAMILIA = "FAMÍLIA"
    ESCOLA = "ESCOLA"
    JUVENTUDE = "JUVENTUDE"
    DESENVOLVIMENTO = "DESENVOLVIMENTO"
    TRABALHO_COMERCIO = "TRABALHO/ COMÉRCIO"
    FINALIZACAO = "FINALIZAÇÃO"


def aggregate_sample_dialogues(mupe_df: pd.DataFrame, audio_id: int) -> tuple[pd.DataFrame, list[int], str]:
    """
    Aggregate contiguous utterances for a given audio_id and detect missing file counters.

    Returns
    -------
    tuple[pd.DataFrame, list[int], str]
        - Aggregated blocks with merged interviewer turns.
        - Sorted list of missing file_id counters.
        - The joined interviewer speaker_code.
    """
    sample = mupe_df.loc[mupe_df["audio_id"] == audio_id].sort_values("start_time").copy()

    if sample.empty:
        raise ValueError(f"No rows found for audio_id={audio_id}")

    join_code, interviewer_codes = get_interviewer_code(sample)
    
    if len(interviewer_codes) > 1:
        sample.loc[sample["speaker_code"].isin(interviewer_codes), "speaker_code"] = join_code

    block_id = (sample["speaker_code"] != sample["speaker_code"].shift()).cumsum()
    
    file_path_extract = sample["file_path"].str.extract(
        r"pc_ma_(?P<mupe_code>hv\d{3})_(?P<file_id>\d+)_")
    
    #TODO log the mupe_code value
    assert all(file_path_extract['mupe_code'] == file_path_extract['mupe_code'].iloc[0]), \
        "Multiple mupe_code values found in the sample."
    
    file_id_series = file_path_extract["file_id"].astype(int)

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
        return df_agg, [], join_code

    file_ids = file_id_series.to_numpy(dtype=int)
    expected = set(range(file_ids.min(), file_ids.max() + 1))
    missing_ids = sorted(expected.difference(file_ids))
    return df_agg, missing_ids, join_code


def get_questions_df(sample_df: pd.DataFrame, interview_code:str) -> pd.DataFrame:
    """
    Filter interview questions for a given interviewer and return their text and start times.

    Parameters
    ----------
    sample_df : pd.DataFrame
        DataFrame containing MUPE utterances with at least the columns
        'speaker_code', 'original_text', and 'start_time'.
    interview_code : str
        The speaker code identifying the interviewer whose turns should be extracted.

    Returns
    -------
    pd.DataFrame
        A copy of the rows where 'speaker_code' matches `interview_code`,
        containing only 'original_text' and 'start_time' columns.

    Raises
    ------
    AssertionError
        If no matching questions are found for the provided `interview_code`.
    """
    questions_df = sample_df[sample_df["speaker_code"] == interview_code][["original_text", "start_time"]].copy()
    assert not questions_df.empty, f"No questions found for interview_code={interview_code}"
    return questions_df


def get_interviewer_code(mupe_sample: pd.DataFrame) -> tuple[str, list[str]]:
    """
    Determine interviewer code(s) from a sample DataFrame.

    Counts occurrences of values in the `speaker_code` column of `mupe_sample`. If
    more than two distinct speaker codes are present, all but the most frequent
    code are considered interviewers and are joined with an underscore to form a
    single code. Otherwise, the least frequent code is used.

    Args:
        mupe_sample (pd.DataFrame): DataFrame containing a `speaker_code` column.

    Returns:
        tuple[str, list[str]]: A tuple where the first element is the combined
        interviewer code string, and the second is a list of individual interviewer
        codes.
    """
    speaker_counts = mupe_sample["speaker_code"].value_counts()

    if len(speaker_counts) > 2:
        interviewer_codes = speaker_counts.index[1:]
        join_code:str = "_".join(interviewer_codes)
    else:
        join_code:str = speaker_counts.index[-1]
        interviewer_codes = [join_code]

    return join_code, list(interviewer_codes)


def split_interview_questions(sample_df: pd.DataFrame, interviewer_code:str) -> tuple[InterviewSegmentation, pd.DataFrame] | tuple[None, None]:
    """
    Segment interviewer utterances into the official interview script structure using a Gemini model.
    This function extracts all questions asked by a given interviewer from a MUPE sample DataFrame,
    formats them with their timestamps, and sends them—together with the reference interview script—
    to a Vertex AI Gemini model for automatic section/subsection assignment. It returns the parsed
    segmentation alongside the questions DataFrame. If the model call fails, it returns (None, None).
    
    Parameters
    ----------
    sample_df : pd.DataFrame
        MUPE utterances containing at least `speaker_code`, `original_text`, and `start_time`.
    interviewer_code : str
        The speaker code of the interviewer whose questions should be segmented.
    
    Returns
    -------
    tuple[InterviewSegmentation, pd.DataFrame] | tuple[None, None]
        A tuple with the structured segmentation result and the interviewer questions DataFrame,
        or (None, None) if the model invocation fails.
    
    Notes
    -----
    - Requires the environment variable `VERTEX_AI_API_KEY` to authenticate with Vertex AI.
    - Relies on the local `./roteiro_entrevista.md` file for the base interview script.
    """
    questions_list = []

    questions_df = get_questions_df(sample_df, interviewer_code)

    for idx, row in questions_df.iterrows():
        questions_list.append(f"{idx} - {int(row.start_time//60):02d}:{int(row.start_time%60):02d} - {row.original_text}")

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
    5. Não utilize caracteres de marcação Markdown (ex: #, ##, etc) nos títulos e subtítulos.

    ROTEIRO BASE:
    {roteiro_entrevista_md}

    TRANSCRIÇÃO PARA SEGMENTAR:
    {"\n".join(questions_list)}
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
        return response_parsed, questions_df
    except Exception as e:
        rich.print(f"[red]Error running Vertex AI:[/red] {e}")
        return None, None
    

def classify_questions(
    questions_parsed: InterviewSegmentation,
    inter_questions: pd.DataFrame,
    level: str | None = None,
) -> pd.DataFrame:
    """
    Attach classification columns to the questions DataFrame.

    Parameters
    ----------
    questions_parsed : InterviewSegmentation
        Parsed segmentation object.
    inter_questions : pd.DataFrame
        DataFrame with questions; its index must correspond to the parsed IDs.
    level : str | None, optional
        If "section", only adds a 'section' column.
        If "subsection", only adds a 'subsection' column.
        If None (default), adds both.

    Returns
    -------
    pd.DataFrame
        Copy of inter_questions with classification columns.
    """
    if level not in {"section", "subsection", None}:
        raise ValueError("level must be 'section', 'subsection', or None")

    id2cls: dict[int, tuple[ClassLabel, ClassLabel, str]] = {}
    for seg in questions_parsed.segments:
        for sub in seg.subsections:
            for item in sub.items:
                try:
                    id2cls[item.id] = (
                        ClassLabel(seg.title),
                        ClassLabel(sub.subtitle),
                        item.timestamp,
                    )
                except ValueError as e:
                    try:
                        rich.print(f"[yellow] Warning [/yellow]: {e} for item id={item.id}, title='{seg.title}', subtitle='{sub.subtitle}'")
                        id2cls[item.id] = (
                            ClassLabel(seg.title),
                            ClassLabel(seg.title),
                            item.timestamp,
                        )
                    except ValueError as e:
                        rich.print(f"[red] Error [/red]: {e} for item id={item.id}, title='{seg.title}', subtitle='{sub.subtitle}'")
                        raise e
                    except Exception as e:
                        rich.print(f"[red] Error [/red]: {e} for item id={item.id}, title='{seg.title}', subtitle='{sub.subtitle}'")
                        raise e
                except Exception as e:
                    rich.print(f"[red] Error [/red]: {e} for item id={item.id}, title='{seg.title}', subtitle='{sub.subtitle}'")
                    raise e
    missing = set(inter_questions.index) - set(id2cls.keys())
    if missing:
        raise ValueError(f"Unclassified question ids: {sorted(missing)}")

    df = inter_questions.copy()
    if level in (None, "section"):
        df["section"] = df.index.map(lambda i: id2cls[i][0])
    if level in (None, "subsection"):
        df["subsection"] = df.index.map(lambda i: id2cls[i][1])
    return df