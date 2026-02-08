# Specification: Adapt MuPe to DailyTalk Specifications

## Overview
This track focuses on the core data engineering task of adapting the MuPe (Multimodal Portuguese Corpus) dataset to follow the structural and metadata rules defined by the DailyTalk paper. This adaptation is critical for subsequent TTS model training.

## Requirements
- **Selection:** Filter MuPe speakers to include only those from São Paulo capital.
- **Dialogue Reconstruction:** Group and concatenate individual audio segments from MuPe into cohesive dialogues.
- **Anonymization:** Ensure the final dataset preserves the anonymity provided by the original MuPe dataset.
- **DailyTalk Alignment:** Format all output metadata (JSON/CSV) and audio directory structures to match the DailyTalk reference exactly.

## Technical Constraints
- High-fidelity audio processing (preserving sampling rate/bit depth).
- Modular Python pipeline following the project's existing architecture.
- Adherence to `conductor/workflow.md` (80% test coverage).
