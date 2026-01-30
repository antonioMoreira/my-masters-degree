import re
from pathlib import Path

import pdfplumber
import pandas as pd

def parse_interview_pdf(pdf_path: Path):
    """
    Parses a Museu da Pessoa style PDF to extract Questions (P) and Answers (R).
    Returns a Pandas DataFrame.
    """
    
    # 1. Extract raw text from all pages
    full_text_lines: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                full_text_lines.extend(lines)

    # 2. Logic to parse lines into Questions and Answers
    data = []
    
    # Counters for identifiers (p1, r1, p2, r2...)
    p_counter = 0
    r_counter = 0
    
    current_type = None # 'p' or 'r'
    current_buffer = [] # Holds the lines of text for the current block
    
    # Patterns to identify headers/footers to ignore
    # Matches dates like "1/29/26, 8:18 PM" or URLs or "Page X/Y"
    ignore_patterns = [
        r"^\d{1,2}/\d{1,2}/\d{2,4}.*Museu da Pessoa", # Header date
        r"^https?://",                                 # Footer URL
        r"^\d+/\d+$",                                  # Page numbers (e.g., 1/21)
        r"^Adilson Show$",                             # Title repetition
        r"^autoria: Museu da Pessoa",                  # Metadata
    ]

    for line in full_text_lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip header/footer noise
        if any(re.search(pat, line) for pat in ignore_patterns):
            continue

        # Check if line starts with Question (P -)
        if line.startswith("P -"):
            # Save previous block if exists
            if current_type:
                joined_text = " ".join(current_buffer).strip()
                # Create identifier based on type (p or r) and its counter
                ident = f"{current_type}{p_counter if current_type == 'p' else r_counter}"
                data.append({"Identifier": ident, "Text": joined_text})

            # Start new Question block
            p_counter += 1
            current_type = 'p'
            current_buffer = [line[3:].strip()] # Remove "P - "

        # Check if line starts with Answer (R -)
        elif line.startswith("R -"):
            # Save previous block if exists
            if current_type:
                joined_text = " ".join(current_buffer).strip()
                ident = f"{current_type}{p_counter if current_type == 'p' else r_counter}"
                data.append({"Identifier": ident, "Text": joined_text})

            # Start new Answer block
            r_counter += 1
            current_type = 'r'
            current_buffer = [line[3:].strip()] # Remove "R - "

        else:
            # It's a continuation of the previous block
            if current_type:
                current_buffer.append(line)

    # 3. Save the very last block
    if current_type and current_buffer:
        joined_text = " ".join(current_buffer).strip()
        ident = f"{current_type}{p_counter if current_type == 'p' else r_counter}"
        data.append({"Identifier": ident, "Text": joined_text})

    # 4. Create DataFrame
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # --- Usage Example ---
    # Assuming you have a list of files or a single file
    pdf_filename = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/mupe-adilson.pdf")  # Replace with your actual file path
    assert pdf_filename.exists(), f"File {pdf_filename} does not exist."

    try:
        df_result = parse_interview_pdf(pdf_filename)
        
        # Display the first few rows
        print(df_result.head())
        
        # Export to CSV if needed
        output_folder = Path("/home/antonio-moreira/Documents/my-masters-degree/notebooks/datasets/mupe-from-pdf")
        assert output_folder.exists(), f"Output folder {output_folder} does not exist."
        output_file = output_folder / "interview_output.csv"
        df_result.to_csv(output_file, index=False)
        
    except Exception as e:
        print(f"Error processing file: {e}")