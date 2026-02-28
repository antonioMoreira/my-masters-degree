# Implementation Plan: Obtaining samples from the mupetalks.csv dataset [checkpoint: d7f4c37]

## Phase 1: Project Setup [checkpoint: b6ba4ca]
- [x] Task: Create test file `tests/test_sampling_mupetalks.py` with basic setup. f1953ab
- [x] Task: Create script stub `my_masters_degree/sampling_mupetalks.py`. f1953ab
- [x] Task: Conductor - User Manual Verification 'Project Setup' (Protocol in workflow.md) b6ba4ca

## Phase 2: Metadata Extraction (TDD) [checkpoint: d7f4c37]
- [x] Task: Write failing tests for reading CSV (`notebooks/mupetalk_train.csv`) and filtering 5 dialogues of one speaker. 16dbbb7
- [x] Task: Implement CSV reading and filtering logic in `my_masters_degree/sampling_mupetalks.py`. 16dbbb7
- [x] Task: Conductor - User Manual Verification 'Metadata Extraction (TDD)' (Protocol in workflow.md) d7f4c37

## Phase 3: Audio Processing (TDD) [checkpoint: d7f4c37]
- [x] Task: Write failing tests for uncompressing parquet files (mocking filesystem). 16dbbb7
- [x] Task: Write failing tests for concatenating audio segments with `PyAV` (mocking PyAV). 16dbbb7
- [x] Task: Implement parquet uncompression logic in `my_masters_degree/sampling_mupetalks.py`. 16dbbb7
- [x] Task: Implement `PyAV` audio joining logic in `my_masters_degree/sampling_mupetalks.py`. 16dbbb7
- [x] Task: Conductor - User Manual Verification 'Audio Processing (TDD)' (Protocol in workflow.md) d7f4c37

## Phase 4: Output Generation and Final Integration [checkpoint: d7f4c37]
- [x] Task: Write tests for exporting dialogues/metadata to JSON or TSV in `my_masters_degree/samples`. 16dbbb7
- [x] Task: Implement output export logic (audio files and JSON/TSV) in `my_masters_degree/sampling_mupetalks.py`. 16dbbb7
- [x] Task: Implement main execution block integrating metadata, audio processing, and exporting. 16dbbb7
- [x] Task: Run script using `uv run python my_masters_degree/sampling_mupetalks.py` to ensure it works end-to-end. a23b6db
- [x] Task: Conductor - User Manual Verification 'Output Generation and Final Integration' (Protocol in workflow.md) d7f4c37
