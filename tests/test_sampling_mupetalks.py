import pytest
import pandas as pd
import tempfile
import os
import io
import json
import numpy as np
import soundfile as sf
from my_masters_degree.sampling_mupetalks import get_speaker_dialogues, join_audio_segments

@pytest.fixture
def mock_csv_path():
    data = {
        'file_path': ["['train/1.wav']", "['train/2.wav']", "['train/3.wav']", "['train/4.wav']", "['train/5.wav']", "['train/6.wav']", "['train/7.wav']"],
        'speaker_code': ['SPK1', 'SPK1', 'SPK1', 'SPK1', 'SPK1', 'SPK1', 'SPK2'],
        'group_id': [1, 1, 2, 2, 3, 4, 5],
        'start_time': [0, 5, 10, 15, 20, 25, 30],
        'original_text': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
        'interview_id': ['I1', 'I1', 'I1', 'I1', 'I2', 'I3', 'I4']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as tmp:
        df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name
        
    yield tmp_path
    
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

def test_get_speaker_dialogues(mock_csv_path):
    dialogues = get_speaker_dialogues(mock_csv_path, 'SPK1', num_dialogues=3)
    assert len(dialogues) == 3 # I1, I2, I3
    assert dialogues[0]['interview_id'] == 'I1'
    assert len(dialogues[0]['groups']) == 2 # group_id 1 and 2
    
    with pytest.raises(ValueError):
        get_speaker_dialogues(mock_csv_path, 'SPK1', num_dialogues=5)

def test_join_audio_segments():
    sr = 16000
    d1 = np.zeros(sr)
    d2 = np.ones(sr) * 0.5
    
    b1 = io.BytesIO()
    sf.write(b1, d1, sr, format='WAV', subtype='PCM_16')
    b2 = io.BytesIO()
    sf.write(b2, d2, sr, format='WAV', subtype='PCM_16')
    
    combined, out_sr = join_audio_segments([b1.getvalue(), b2.getvalue()])
    assert len(combined) == 2 * sr
    assert out_sr == sr
    assert np.allclose(combined[:sr], 0, atol=1e-4)
    assert np.allclose(combined[sr:], 0.5, atol=1e-4)
