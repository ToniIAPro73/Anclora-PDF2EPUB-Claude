import os
from typing import List, Dict


def evaluate_sequences(sequences: List[List[str]]) -> List[Dict[str, object]]:
    return [{"steps": seq, "score": 0} for seq in sequences]


def run_pipeline(pdf_path: str, output_path: str) -> Dict[str, object]:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(b'')
    return {"success": True, "output": output_path, "metrics": []}
