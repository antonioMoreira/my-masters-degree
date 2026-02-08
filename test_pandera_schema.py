
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

import pandas as pd
import pandera as pa
from my_masters_degree.postprocess_dataset import load_and_validate_mupetalk, MupeTalkSchema

def test_schema():
    csv_path = "notebooks/mupetalk_train.csv"
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    print(f"Loading {csv_path}...", flush=True)
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows.", flush=True)
    
    # Test with first 5 rows
    df_head = df.head(5)
    
    try:
        validated_df = load_and_validate_mupetalk(df_head)
        print(f"Successfully validated {len(validated_df)} rows.", flush=True)
        
        # Verify types
        first_row = validated_df.iloc[0]
        if not isinstance(first_row.file_id, list):
            print(f"Row 0 file_id is not a list: {type(first_row.file_id)}", flush=True)
            sys.exit(1)
            
        print("Schema validation successful!", flush=True)
            
    except pa.errors.SchemaError as e:
        print(f"Schema validation failed: {e}", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_schema()
