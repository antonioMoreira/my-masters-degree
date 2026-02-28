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
    Reads the metadata CSV and extracts a specified number of dialogues (interviews)
    for a given speaker.
    """
    df = pd.read_csv(csv_path)
    
    # We want 5 distinct interviews for this speaker
    speaker_interviews = df[df['speaker_code'] == speaker_code]['interview_id'].unique()
    
    if len(speaker_interviews) < num_dialogues:
        raise ValueError(f"Speaker {speaker_code} participates in only {len(speaker_interviews)} interviews, but {num_dialogues} were requested.")
    
    selected_interview_ids = speaker_interviews[:num_dialogues]
    
    dialogues = []
    for interview_id in selected_interview_ids:
        interview_df = df[df['interview_id'] == interview_id].sort_values(['group_id', 'start_time'])
        
        # Group by group_id
        groups = []
        for group_id, group_df in interview_df.groupby('group_id'):
            groups.append({
                'group_id': int(group_id),
                'turns': group_df.to_dict(orient='records')
            })
            
        dialogues.append({
            'interview_id': interview_id,
            'groups': groups
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

def parse_paths(fp: str) -> List[str]:
    # Replace PosixPath string representation to standard python list of strings
    if isinstance(fp, str):
        fp = fp.replace("PosixPath('", "'").replace("')", "'")
        return ast.literal_eval(fp)
    return [fp]

def main() -> None:
    csv_path = 'notebooks/mupetalk_train_v2.csv'
    parquet_dir = 'notebooks/datasets/CORAA-MUPE'
    output_dir = 'my_masters_degree/samples'
    # Using EBP007 since it has 4 interviews
    speaker_code = 'EBP007'
    
    print(f"Extracting 4 interviews for speaker {speaker_code}...")
    interviews = get_speaker_dialogues(csv_path, speaker_code, num_dialogues=4)
    
    all_needed_files = []
    for interview in interviews:
        for group in interview['groups']:
            for turn in group['turns']:
                paths = parse_paths(turn['file_path'])
                all_needed_files.extend(paths)
            
    unique_files = list(set(all_needed_files))
    print(f"Searching for {len(unique_files)} unique audio files in parquets...")
    audio_map = extract_audio_from_parquets(unique_files, parquet_dir)
    
    if len(audio_map) < len(unique_files):
        missing = set(unique_files) - set(audio_map.keys())
        print(f"Warning: {len(missing)} files not found in parquets: {list(missing)[:5]}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, interview in enumerate(interviews):
        print(f"Processing interview {i+1}/{len(interviews)} (interview_id: {interview['interview_id']})...")
        
        sample_dir = os.path.join(output_dir, f"sample_{i}")
        os.makedirs(sample_dir, exist_ok=True)
        
        groups_dir = os.path.join(sample_dir, f"sample_{i}_groups")
        os.makedirs(groups_dir, exist_ok=True)
        
        interview_audio_bytes = []
        interview_metadata = []
        
        for group in interview['groups']:
            group_audio_bytes = []
            group_metadata = group['turns']
            interview_metadata.extend(group['turns'])
            
            for turn in group['turns']:
                paths = parse_paths(turn['file_path'])
                for p in paths:
                    if p in audio_map:
                        group_audio_bytes.append(audio_map[p])
                        interview_audio_bytes.append(audio_map[p])
            
            # Save group
            if group_audio_bytes:
                audio_data, sr = join_audio_segments(group_audio_bytes)
                group_id = group['group_id']
                
                audio_path = os.path.join(groups_dir, f"sample_{i}_id{group_id}.wav")
                sf.write(audio_path, audio_data, sr)
                
                meta_path = os.path.join(groups_dir, f"sample_{i}_id{group_id}.json")
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(group_metadata, f, indent=2, ensure_ascii=False)
        
        # Save interview
        if interview_audio_bytes:
            audio_data, sr = join_audio_segments(interview_audio_bytes)
            
            audio_path = os.path.join(sample_dir, f"sample_{i}.wav")
            sf.write(audio_path, audio_data, sr)
            
            meta_path = os.path.join(sample_dir, f"sample_{i}.json")
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(interview_metadata, f, indent=2, ensure_ascii=False)
                
        print(f"Saved interview sample {i} to {sample_dir}")

if __name__ == "__main__":
    main()
