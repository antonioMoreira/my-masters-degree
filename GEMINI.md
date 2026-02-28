# Project: my_masters_degree

## Overview
This project serves as the codebase for a Master's degree research focused on adapting the **MuPe dataset** (Portuguese speech data) to fit the specifications of the **DailyTalk** paper. The ultimate goal is to train a Text-to-Speech (TTS) model that captures conversational features in the Portuguese language.

## Key Goals
1.  **Metadata Filtering:** Select specific subgroups (e.g., speakers from SP capital).
2.  **Anonymization:** Remove sensitive introductory segments.
3.  **Dialogue Reconstruction:** Concatenate audio segments into conversational dialogues.
4.  **Standardization:** Format the dataset to match DailyTalk specifications.

## Architecture & Structure

### Core Package (`my_masters_degree/`)
*   **`main.py`**: The entry point for the data processing pipeline. It orchestrates reading the raw dataset, filtering based on metadata, running the segmentation logic, and saving the results.
*   **`process_dataset.py`**: Contains the core logic for:
    *   Aggregating contiguous utterances.
    *   Segmenting interviews using **Google Vertex AI (Gemini)** to map questions to a standardized script (`roteiro_entrevista.md`).
    *   Classifying questions into sections/subsections.
    *   Post-processing (removing identification, handling missing files).
*   **`extract_from_pdf.py`**: Utility for extracting information from PDF documents.
*   **`utils.py`**: General utility functions.

### Data & Exploration (`notebooks/`)
*   Contains Jupyter notebooks (`.ipynb`) for data exploration and validation.
*   Stores intermediate and output datasets (Excel, CSV, JSON segmentations).
*   **Key Files:**
    *   `roteiro_entrevista.md`: The reference interview script used for segmentation.
    *   `mupetalk_train.csv`: The final aggregated output (CSV).
    *   `interview_segmentations/*.json`: Cached segmentation results from the LLM.

### Project Management (`conductor/`)
*   Contains the product definition (`product.md`), tech stack (`tech-stack.md`), and tracking documents for the research progress.

## Setup & Development

### Prerequisites
*   **Python**: >= 3.13
*   **Dependency Manager**: `uv` (recommended) or `pip`.
*   **API Keys**: `VERTEX_AI_API_KEY` is required for the segmentation logic in `process_dataset.py` to access Google Gemini models.

### Installation
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install .
```

### Running the Pipeline
The main processing pipeline can be triggered via the `main.py` script:

```bash
# Ensure VERTEX_AI_API_KEY is set
export VERTEX_AI_API_KEY="your_key_here"

# Run the main processing script
python -m my_masters_degree.main
```

### Testing
Tests are located in the `tests/` directory.
```bash
# Run tests (example)
pytest
```

## Conventions
*   **Type Hinting**: Extensive use of Python type hints (`typing`, `pydantic`).
*   **Configuration**: Dependencies and build config are managed in `pyproject.toml`.
*   **Output**: Uses `rich` for formatted terminal output.
*   **Data Handling**: Heavily relies on `pandas` for tabular data and `pydantic` for data validation/serialization.
