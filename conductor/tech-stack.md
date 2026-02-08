# Technology Stack

## Core Language & Runtime
- **Python (>= 3.13):** Primary programming language, leveraging high-performance features and modern syntax.

## Data Processing & Analysis
- **Pandas & NumPy:** Essential libraries for large-scale dataset manipulation, filtering, and numerical analysis.
- **OpenPyXL:** Used for reading and writing Excel files, facilitating metadata management.

## Machine Learning & Audio Processing
- **PyTorch:** The foundational framework for training and validating the TTS model.
- **TorchCodec & SciPy:** Specialized tools for high-fidelity audio decoding and signal processing.
- **Datasets (Hugging Face):** Streamlined management and versioning of the MuPe and DailyTalk formatted data.

## Research & Validation
- **WERpy:** Used for Word Error Rate (WER) analysis to objectively measure TTS performance.
- **Matplotlib:** For generating visualizations of dataset statistics and model performance.

## AI & Automation
- **Google GenAI:** Integration of LLMs for sophisticated data labeling, extraction, or automated analysis tasks.
- **PDFPlumber:** Specialized for extracting structured metadata from legacy PDF documentation (e.g., MuPe interview details).

## Utilities & Infrastructure
- **Pydantic:** Ensures data integrity through strict type validation for configuration and dataset schemas.
- **Python-Dotenv:** Manages sensitive environment variables and project configurations.
- **Rich:** Enhances CLI output for better progress tracking and debugging during long-running processing tasks.
