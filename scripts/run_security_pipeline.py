"""
Top-level entrypoint for running the MyCRM Enterprise Security Pipeline.
Can be executed locally or inside CI/CD runners.
"""
import sys
import os

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.security_pipeline.security_orchestrator import main

if __name__ == '__main__':
    main()
