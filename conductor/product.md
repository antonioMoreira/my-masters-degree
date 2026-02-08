# Initial Concept
The main objective of this project is to adapt the MuPe dataset to fit the specifications of DailyTalk, which is the reference paper. Subsequently, a TTS model will be trained to validate whether the new dataset was able to capture conversational features in the Portuguese language.

# Product Definition

## Goals
- Adapt the MuPe dataset to fit the specifications of the DailyTalk reference paper.
- Train a Text-to-Speech (TTS) model to validate the dataset's ability to capture conversational features in Portuguese.
- Establish a reproducible pipeline for speech dataset adaptation.

## Target Audience
- Master's degree review committee and academic collaborators.

## Core Features
- **Metadata Filtering:** Automated selection of subgroups (e.g., SP capital speakers) from MuPe.
- **Anonymization:** Logic to skip sensitive introductory segments to ensure interviewee anonymity.
- **Audio Dialogue Reconstruction:** Concatenation and processing of audio segments to create conversational dialogues.
- **Standardization:** Formatting and alignment of the generated dataset to match DailyTalk rules and specifications.

## Deliverables
- A finalized, filtered, and standardized version of the MuPe dataset ready for TTS training.
- A trained TTS model capable of demonstrating conversational nuances in Portuguese.

## Constraints
- Strict adherence to the formatting and metadata structure defined in the DailyTalk paper.
