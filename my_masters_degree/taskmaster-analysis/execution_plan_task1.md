# Execution Plan - Taskmaster-1 EDA

This plan outlines the steps to perform an Exploratory Data Analysis (EDA) on the Taskmaster-1 dataset from HuggingFace.

## Steps

1. **Environment Verification**: Ensure `uv` is set up and required libraries (`datasets`, `pandas`, `matplotlib`, `seaborn`) are available.
2. **Script Creation**: Develop `my_masters_degree/taskmaster-analysis/eda_taskmaster_hf.py` with the following logic:
    - Load `google-research-datasets/taskmaster1` using HuggingFace `datasets`.
    - Process and aggregate splits (if applicable).
    - Calculate statistics:
        - Total dialogues.
        - Turns per dialogue (mean, median).
        - Speaker distribution.
    - Generate visualizations:
        - Histogram of turns per dialogue.
        - Bar chart of speaker distribution.
    - Save results to `my_masters_degree/taskmaster-analysis/results/`.
3. **Execution**: Run the script using `uv run`.
4. **Verification**: Confirm the generation of `stats.txt` and PNG files.

## Dependencies
- `datasets`
- `pandas`
- `matplotlib`
- `seaborn`
