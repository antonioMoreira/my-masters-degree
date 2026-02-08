# Implementation Plan: Adapt MuPe to DailyTalk Specifications

## Phase 1: Setup and Filtering
- [ ] Task: Project Scaffolding for Dataset Pipeline
    - [ ] Create directory structure for the pipeline (`my_masters_degree/pipeline/`).
    - [ ] Define shared Pydantic models for MuPe and DailyTalk schemas.
- [ ] Task: Metadata Filtering Logic
    - [ ] Write tests for the SP capital speaker filter.
    - [ ] Implement the filtering logic in `my_masters_degree/pipeline/filter.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Setup and Filtering' (Protocol in workflow.md)

## Phase 2: Audio Processing and Dialogue Reconstruction
- [ ] Task: Dialogue Grouping Logic
    - [ ] Write tests for grouping segments into dialogues based on MuPe session metadata.
    - [ ] Implement grouping logic in `my_masters_degree/pipeline/dialogue.py`.
- [ ] Task: Audio Concatenation
    - [ ] Write tests for high-fidelity audio concatenation using `torchcodec` or `scipy`.
    - [ ] Implement concatenation logic with verification of sampling rates.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Audio Processing and Dialogue Reconstruction' (Protocol in workflow.md)

## Phase 3: DailyTalk Formatting and Validation
- [ ] Task: DailyTalk Schema Exporter
    - [ ] Write tests for the DailyTalk metadata format exporter.
    - [ ] Implement exporter logic to generate JSON/CSV files as per DailyTalk specs.
- [ ] Task: Automated Pipeline Validation
    - [ ] Implement a validation script to check the final output against requirements.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: DailyTalk Formatting and Validation' (Protocol in workflow.md)
