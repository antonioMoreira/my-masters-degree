import pandas as pd
import os
import io
import json
import ast
from typing import List, Dict, Any, Tuple
import soundfile as sf
import numpy as np

def get_speaker_dialogues(csv_path: str, speaker_code: str, num_dialogues: int = 5) -> List[Dict[str, Any]]:
    """
    Reads the metadata CSV and extracts a specified number of dialogues
    for a given speaker. A 'dialogue' is considered a unique 'group_id' for that speaker.
    """
    df = pd.read_csv(csv_path)
    
    # Find group_ids where the speaker participates
    speaker_group_ids = df[df['speaker_code'] == speaker_code]['group_id'].unique()
    
    if len(speaker_group_ids) < num_dialogues:
        raise ValueError(f"Speaker {speaker_code} participates in only {len(speaker_group_ids)} dialogues, but {num_dialogues} were requested.")
    
    selected_group_ids = speaker_group_ids[:num_dialogues]
    
    dialogues = []
    for group_id in selected_group_ids:
        group_df = df[df['group_id'] == group_id].sort_values(['group_id', 'start_time'])
        dialogues.append({
            'group_id': int(group_id),
            'turns': group_df.to_dict(orient='records')
        })
        
    return dialogues

def extract_audio_from_parquets(file_paths: List[str], parquet_dir: str) -> Dict[str, bytes]:
    """
    Finds and extracts audio bytes for a list of file paths from parquet files.
    """
    audio_map = {}
    needed_paths = set(file_paths)
    
    data_dir = os.path.join(parquet_dir, 'data')
    parquet_files = [f for f in os.listdir(data_dir) if f.endswith('.parquet') and 'train' in f]
    
    for pf in sorted(parquet_files):
        if not needed_paths:
            break
            
        full_path = os.path.join(data_dir, pf)
        # Use a more efficient way if possible, but for 74 files it's okay for once
        df = pd.read_parquet(full_path, columns=['file_path', 'audio'])
        
        mask = df['file_path'].isin(needed_paths)
        matches = df[mask]
        
        for _, row in matches.iterrows():
            audio_map[row['file_path']] = row['audio']['bytes']
            
        found_now = set(matches['file_path'])
        needed_paths -= found_now
            
    return audio_map

def join_audio_segments(audio_bytes_list: List[bytes]) -> Tuple[np.ndarray, int]:
    """
    Joins multiple audio byte segments into a single numpy array.
    Returns (audio_data, samplerate).
    """
    all_data = []
    samplerate = None
    
    for b in audio_bytes_list:
        data, sr = sf.read(io.BytesIO(b))
        if samplerate is None:
            samplerate = sr
        elif samplerate != sr:
            raise ValueError(f"Sample rate mismatch: {samplerate} != {sr}")
        all_data.append(data)
    
    if not all_data:
        return np.array([]), 0
        
    combined = np.concatenate(all_data)
    return combined, samplerate

def save_sample(output_dir: str, dialogue_idx: int, audio_data: np.ndarray, samplerate: int, metadata: List[Dict[str, Any]]) -> str:
    """
    Saves audio and metadata for a dialogue sample.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    audio_filename = f"sample_{dialogue_idx}.wav"
    audio_path = os.path.join(output_dir, audio_filename)
    sf.write(audio_path, audio_data, samplerate)
    
    meta_filename = f"sample_{dialogue_idx}.json"
    meta_path = os.path.join(output_dir, meta_filename)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    return audio_path

def main() -> None:
    csv_path = 'notebooks/mupetalk_train.csv'
    parquet_dir = 'notebooks/datasets/CORAA-MUPE'
    output_dir = 'my_masters_degree/samples'
    # Using MA_HV229 as seen in the CSV head earlier
    speaker_code = 'MA_HV229'
    
    print(f"Extracting 5 dialogues for speaker {speaker_code}...")
    dialogues = get_speaker_dialogues(csv_path, speaker_code, num_dialogues=5)
    
    all_needed_files = []
    for d in dialogues:
        for turn in d['turns']:
            # Handle potential non-list strings if any, but CSV head showed "['path']"
            fp = turn['file_path']
            if isinstance(fp, str) and fp.startswith('['):
                paths = ast.literal_eval(fp)
            else:
                paths = [fp]
            all_needed_files.extend(paths)
            
    unique_files = list(set(all_needed_files))
    print(f"Searching for {len(unique_files)} unique audio files in parquets...")
    audio_map = extract_audio_from_parquets(unique_files, parquet_dir)
    
    if len(audio_map) < len(unique_files):
        missing = set(unique_files) - set(audio_map.keys())
        print(f"Warning: {len(missing)} files not found in parquets: {list(missing)[:5]}...")
    
    for i, d in enumerate(dialogues):
        print(f"Processing dialogue {i+1}/{len(dialogues)} (group_id: {d['group_id']})...")
        dialogue_audio_bytes = []
        for turn in d['turns']:
            fp = turn['file_path']
            if isinstance(fp, str) and fp.startswith('['):
                paths = ast.literal_eval(fp)
            else:
                paths = [fp]
                
            for p in paths:
                if p in audio_map:
                    dialogue_audio_bytes.append(audio_map[p])
        
        if dialogue_audio_bytes:
            audio_data, sr = join_audio_segments(dialogue_audio_bytes)
            saved_path = save_sample(output_dir, i, audio_data, sr, d['turns'])
            print(f"Saved sample to {saved_path}")
        else:
            print(f"Skipping dialogue {i+1} as no audio was found.")

if __name__ == "__main__":
    main()
