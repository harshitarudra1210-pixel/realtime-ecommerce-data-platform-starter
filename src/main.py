"""Run the local e-commerce batch pipeline: python -m src.main"""
import json
from src.pipeline import run_pipeline

if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
