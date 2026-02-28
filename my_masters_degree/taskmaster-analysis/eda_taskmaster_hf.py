import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import load_dataset
from pathlib import Path
import json

# Paths
RESULTS_DIR = Path("./my_masters_degree/taskmaster-analysis/results")
DATA_DIR = Path("./my_masters_degree/taskmaster-analysis/data")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("Loading Taskmaster-1 data from URLs...")
    
    # URLs to raw JSON files
    data_files = {
        "self_dialogs": "https://raw.githubusercontent.com/google-research-datasets/Taskmaster/master/TM-1-2019/self-dialogs.json",
        "woz_dialogs": "https://raw.githubusercontent.com/google-research-datasets/Taskmaster/master/TM-1-2019/woz-dialogs.json"
    }

    try:
        # Load datasets directly from URLs
        dataset = load_dataset("json", data_files=data_files)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Combine splits
    all_data = []
    for split in dataset.keys():
        print(f"Processing split: {split}")
        df_split = dataset[split].to_pandas()
        all_data.append(df_split)
    
    if not all_data:
        print("No data found.")
        return
        
    df = pd.concat(all_data, ignore_index=True)
    
    # Statistics
    total_dialogues = len(df)
    
    # The dataset has an 'utterances' column which is a list of dicts/structs
    # Each dict has 'speaker' and 'text'
    def count_turns(utterances):
        if utterances is not None:
            # Handle numpy arrays if loaded that way
            if hasattr(utterances, 'tolist'):
                utterances = utterances.tolist()
            return len(utterances)
        return 0

    df['num_turns'] = df['utterances'].apply(count_turns)
    
    mean_turns = df['num_turns'].mean()
    median_turns = df['num_turns'].median()
    
    # Speaker distribution
    all_speakers = []
    
    # For safety, iterate carefully
    for utterances in df['utterances']:
        if utterances is not None:
            # If it's a numpy array of objects (from datasets), convert to list
            if hasattr(utterances, 'tolist'):
                utterances = utterances.tolist()
            
            for u in utterances:
                # u might be a dict or a Row object
                if isinstance(u, dict):
                     speaker = u.get('speaker', 'unknown')
                else:
                     # If it's a Row/Struct from pyarrow/datasets
                     speaker = getattr(u, 'speaker', 'unknown') if hasattr(u, 'speaker') else u.get('speaker', 'unknown')
                
                if speaker:
                    all_speakers.append(speaker)
                else:
                    all_speakers.append('unknown')
    
    speaker_counts = pd.Series(all_speakers).value_counts()
    
    # Save stats
    stats_file = RESULTS_DIR / "stats.txt"
    with open(stats_file, "w") as f:
        f.write("Taskmaster-1 (2019) EDA Results\n")
        f.write("==============================\n")
        f.write(f"Total Dialogues: {total_dialogues}\n")
        f.write(f"Mean Turns per Dialogue: {mean_turns:.2f}\n")
        f.write(f"Median Turns per Dialogue: {median_turns:.2f}\n")
        f.write("\nSpeaker Distribution:\n")
        f.write(speaker_counts.to_string())
        f.write("\n")

    print(f"Stats saved to {stats_file}")

    # Visualizations
    sns.set_theme(style="whitegrid")
    
    # 1. Distribution of turns
    plt.figure(figsize=(10, 6))
    sns.histplot(df['num_turns'], bins=30, kde=True, color='skyblue')
    plt.title("Distribution of Turns per Dialogue (Taskmaster-1)")
    plt.xlabel("Number of Turns")
    plt.ylabel("Frequency")
    plt.savefig(RESULTS_DIR / "distribuicao_turnos.png")
    plt.close()

    # 2. Speaker distribution
    plt.figure(figsize=(10, 6))
    # Filter top N speakers if too many (though usually just USER/ASSISTANT)
    if len(speaker_counts) > 10:
        top_speakers = speaker_counts.head(10)
    else:
        top_speakers = speaker_counts
        
    top_speakers.plot(kind='bar', color='skyblue')
    plt.title("Speaker Distribution (Taskmaster-1)")
    plt.xlabel("Speaker Role")
    plt.ylabel("Total Utterances")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "distribuicao_speakers.png")
    plt.close()
    
    print(f"Visualizations saved to {RESULTS_DIR}")

if __name__ == "__main__":
    main()
