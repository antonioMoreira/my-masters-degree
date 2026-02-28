# Implementation Plan: Obtaining samples from the mupetalks.csv dataset

## Phase 1: Project Setup [checkpoint: b6ba4ca]
- [x] Task: Create test file `tests/test_sampling_mupetalks.py` with basic setup. f1953ab
- [x] Task: Create script stub `my_masters_degree/sampling_mupetalks.py`. f1953ab
- [x] Task: Conductor - User Manual Verification 'Project Setup' (Protocol in workflow.md) b6ba4ca

## Phase 2: Metadata Extraction (TDD)
- [ ] Task: Write failing tests for reading CSV (`notebooks/mupetalk_train.csv`) and filtering 5 dialogues of one speaker.
- [ ] Task: Implement CSV reading and filtering logic in `my_masters_degree/sampling_mupetalks.py`.
- [ ] Task: Conductor - User Manual Verification 'Metadata Extraction (TDD)' (Protocol in workflow.md)

## Phase 3: Audio Processing (TDD)
- [ ] Task: Write failing tests for uncompressing parquet files (mocking filesystem).
- [ ] Task: Write failing tests for concatenating audio segments with `PyAV` (mocking PyAV).
- [ ] Task: Implement parquet uncompression logic in `my_masters_degree/sampling_mupetalks.py`.
- [ ] Task: Implement `PyAV` audio joining logic in `my_masters_degree/sampling_mupetalks.py`.
- [ ] Task: Conductor - User Manual Verification 'Audio Processing (TDD)' (Protocol in workflow.md)

## Phase 4: Output Generation and Final Integration
- [ ] Task: Write tests for exporting dialogues/metadata to JSON or TSV in `my_masters_degree/samples`.
- [ ] Task: Implement output export logic (audio files and JSON/TSV) in `my_masters_degree/sampling_mupetalks.py`.
- [ ] Task: Implement main execution block integrating metadata, audio processing, and exporting.
- [ ] Task: Run script using `uv run python my_masters_degree/sampling_mupetalks.py` to ensure it works end-to-end.
- [ ] Task: Conductor - User Manual Verification 'Output Generation and Final Integration' (Protocol in workflow.md)
