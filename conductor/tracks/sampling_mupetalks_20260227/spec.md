# Specification: Obtaining samples from the mupetalks.csv dataset

## Overview
This track focuses on extracting and processing a sample of 5 entire dialogues from a single speaker using the `notebooks/mupetalk_train.csv` metadata file and the audio files located in `notebooks/datasets/CORAA-MUPE`. The script will uncompress parquet files, join the dialogue audios using `PyAV`, and export the final audios and metadata to `my_masters_degree/samples` in JSON or TSV format.

## Functional Requirements
- Read the source `notebooks/mupetalk_train.csv` dataset.
- Extract data for 5 complete dialogues belonging to the *same* speaker.
- Uncompress the necessary audio parquet files from the `notebooks/datasets/CORAA-MUPE` directory.
- Concatenate/join the audio segments of these 5 dialogues using the `PyAV` library.
- Export the joined audio files and their respective dialogues/metadata (as JSON or TSV) to the `my_masters_degree/samples` directory.
- The final implementation script must be located at `my_masters_degree/sampling_mupetalks.py`.
- Run the code using `uv run`.

## Non-Functional Requirements
- The script should be efficient, as uncompressing parquet files can take significant time.
- The code must follow the project's Python style guidelines and use type hinting.

## Acceptance Criteria
- [ ] A script `my_masters_degree/sampling_mupetalks.py` is created.
- [ ] 5 entire dialogues from a single speaker are successfully extracted based on the CSV.
- [ ] The relevant audio parquet files are uncompressed.
- [ ] The audio files for these dialogues are successfully joined using `PyAV`.
- [ ] The final joined audios and metadata (JSON or TSV) are saved in `my_masters_degree/samples`.
- [ ] The logic is covered by unit tests (red-green-refactor cycle).

## Out of Scope
- Extracting the entire dataset; this is strictly limited to 5 dialogues from one speaker.
- Training the TTS model.
