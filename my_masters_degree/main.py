import re
import os
import difflib
from enum import Enum
from pathlib import Path
from typing import List, Tuple, cast, Literal

import rich
import datasets
import numpy as np
import pandas as pd
from google import genai 
# from dotenv import load_dotenv
from google.genai import types
from datasets import Audio
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from pydantic import BaseModel, Field
from matplotlib.colors import ListedColormap
from IPython.display import Audio as ipyAudio

DATASETS_PATH = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/datasets/")
MUPE_GIT_PATH = DATASETS_PATH / "coling-mupe-asr"
PROCESSED_METADATA_PATH = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/mupe_metadata_sp_gender_slice.csv")
INTERVIEW_SEGMENTATIONS_PATH = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/interview_segmentations")
EXCEL_FILES_PATH = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/excel_files/")

assert DATASETS_PATH.exists(), f"DATASETS_PATH does not exist: {DATASETS_PATH}"
assert MUPE_GIT_PATH.exists(), f"MUPE_GIT_PATH does not exist: {MUPE_GIT_PATH}"
assert PROCESSED_METADATA_PATH.exists(), f"PROCESSED_METADATA_PATH does not exist: {PROCESSED_METADATA_PATH}"
assert INTERVIEW_SEGMENTATIONS_PATH.exists(), f"INTERVIEW_SEGMENTATIONS_PATH does not exist: {INTERVIEW_SEGMENTATIONS_PATH}"
assert EXCEL_FILES_PATH.exists(), f"EXCEL_FILES_PATH does not exist: {EXCEL_FILES_PATH}"

custom_colors = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
    "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5",
    "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f",
    "#e5c494", "#b3b3b3", "#1b9e77", "#d95f02", "#7570b3",
    "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666"
]

mupe_cmap = ListedColormap(custom_colors, name="MupeExcelColorMap")
matplotlib.colormaps.register(name="MupeExcelColorMap", cmap=mupe_cmap, force=True)

from process_dataset import (
    aggregate_sample_dialogues,
    classify_questions,
    get_questions_df,
    get_interviewer_code,
    get_group_mapping,
    post_process_mupe_sample,
    split_interview_questions,
    InterviewSegmentation
)


def get_well_behaved_samples(mupe_train: pd.DataFrame, audio_ids: List[int]):
    itvw_codes_list = []

    for audio_id in audio_ids:
        sample = mupe_train[mupe_train["audio_id"] == int(audio_id)].copy()
        join_code, interviewer_codes = get_interviewer_code(sample)
        itvw_codes_list.append([audio_id, join_code, interviewer_codes])

    itvw_codes_df = pd.DataFrame(itvw_codes_list, columns=['audio_id', 'interviewer_join_code', 'interviewer_codes'])
    itvw_codes_df = itvw_codes_df[itvw_codes_df["interviewer_codes"].apply(len) == 1]

    return itvw_codes_df

def highlight_group(row:pd.Series):
    color = group_to_color.get(row["group_id"], "#FFFFFF")
    return [f"background-color: {color}"] * len(row)

if __name__ == "__main__":
    mupe_train_df = pd.read_csv(MUPE_GIT_PATH / "train.csv")
    
    mupe_metadata_sp_df = (
        pd.read_csv(PROCESSED_METADATA_PATH)
        .drop(columns=['interviewer2_gender'])
    )

    mupe_metadata_sp_df = mupe_metadata_sp_df[mupe_metadata_sp_df["split"] == "train"]
    itvw_codes_df = get_well_behaved_samples(
        mupe_train=mupe_train_df,
        audio_ids=mupe_metadata_sp_df['audio_id'].tolist()
    )

    file_name_re = re.compile(r"interview_segmentation_(?P<audio_id>\d+)\.json")
    for json_segmentation in INTERVIEW_SEGMENTATIONS_PATH.glob("interview_segmentation_*.json"):
        file_id = int(file_name_re.match(json_segmentation.name).group("audio_id"))
        mupe_train_sample, missing_ids_sample, itvw_code = aggregate_sample_dialogues(mupe_train_df, audio_id=file_id)
        
        if file_id in itvw_codes_df["audio_id"].values:
            rich.print(f"Processing file for audio_id={file_id} with interview_code={itvw_code}")
            interview_segmentation_sample = InterviewSegmentation.model_validate_json(
                json_segmentation.read_text(encoding="utf-8")
            )
            questions_df_sample = get_questions_df(mupe_train_sample, itvw_code)
        else:
            rich.print(f"Skipping file for audio_id={file_id} not in itvw_codes_df")
            continue

        questions_parsed_classified = classify_questions(
            questions_parsed=interview_segmentation_sample,
            inter_questions=questions_df_sample,
            level="subsection"
        )

        mupe_train_sample_clsfd = mupe_train_sample.merge(
            questions_parsed_classified["subsection"], left_index=True, right_index=True, how="left"
        ).ffill().copy()

        mupe_train_sample_final = post_process_mupe_sample(mupe_train_sample_clsfd)
        
        mapping = get_group_mapping(mupe_train_sample_final)
        mupe_train_sample_final["group_id"] = (
            mupe_train_sample_final.index.map(mapping.get).astype("Int8")
        )

        mupe_train_sample_final.dropna(subset=['group_id'], inplace=True)

        unique_groups = sorted(mupe_train_sample_final["group_id"].unique())
        group_to_color = {g: to_hex(mupe_cmap(i)) for i, g in enumerate(unique_groups)}

        excel_base_name = "mupe_train_sample_{}.xlsx".format(file_id)
        excel_path = EXCEL_FILES_PATH / excel_base_name

        mupe_train_sample_final.style.apply(highlight_group, axis=1).to_excel(excel_path, index=False)
        rich.print(f"Saved processed sample to {excel_path}")