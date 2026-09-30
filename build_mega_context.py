import os
from pathlib import Path

out_file = "/Users/adi/Desktop/DSP Mini Project/mega_report_context.md"

files_to_include = [
    ("REPORT FORMATTING SPECIFICATION (CRITICAL)", "/Users/adi/Desktop/DSP Mini Project/ku_format.md"),
    ("PROJECT COMPREHENSIVE STUDY", "/Users/adi/Desktop/DSP Mini Project/study.md"),
    ("LITERATURE REVIEW", "/Users/adi/Desktop/DSP Mini Project/load_adaptive_iir_literature_review.md"),
    ("PROJECT HISTORY AND CONTEXT", "/Users/adi/Desktop/DSP Mini Project/project_context.md"),
    ("EXISTING LATEX DRAFT (FOR REFERENCE)", "/Users/adi/Desktop/DSP Mini Project/report_v2.tex"),
]

code_dir = Path("/Users/adi/Desktop/DSP Mini Project/load-adaptive-iir/src")
results_dir = Path("/Users/adi/Desktop/DSP Mini Project/load-adaptive-iir/results/tables")
results_summary = Path("/Users/adi/Desktop/DSP Mini Project/load-adaptive-iir/results/compute_benefit_summary.md")

with open(out_file, 'w', encoding='utf-8') as f:
    f.write("# MEGA REPORT CONTEXT FOR EXTERNAL AI AGENT\n\n")
    f.write("You are an AI agent tasked with writing a final project report in LaTeX format.\n")
    f.write("This document contains ALL the context you will need. It is broken into sections.\n")
    f.write("Your goal is to write a complete, compilable .tex file that perfectly follows the rules in the REPORT FORMATTING SPECIFICATION section.\n")
    f.write("Use the PROJECT COMPREHENSIVE STUDY for all theoretical and technical details.\n")
    f.write("Use the SOURCE CODE and EXPERIMENT RESULTS to populate Chapter 3 (Design) and Chapter 4 (Achievements).\n")
    f.write("Use the LITERATURE REVIEW for Chapter 2 (Related Works).\n\n")
    
    for title, filepath in files_to_include:
        f.write(f"\n\n{'='*80}\n")
        f.write(f"--- SECTION: {title} ---\n")
        f.write(f"{'='*80}\n\n")
        try:
            with open(filepath, 'r', encoding='utf-8') as infile:
                f.write(infile.read())
        except Exception as e:
            f.write(f"Error reading file {filepath}: {e}\n")
            
    f.write(f"\n\n{'='*80}\n")
    f.write(f"--- SECTION: SOURCE CODE ---\n")
    f.write(f"{'='*80}\n\n")
    
    for py_file in code_dir.glob('*.py'):
        f.write(f"\n\n### File: {py_file.name}\n\n```python\n")
        try:
            with open(py_file, 'r', encoding='utf-8') as infile:
                f.write(infile.read())
        except Exception as e:
            f.write(f"Error reading file {py_file}: {e}\n")
        f.write("\n```\n")
        
    f.write(f"\n\n{'='*80}\n")
    f.write(f"--- SECTION: EXPERIMENT RESULTS ---\n")
    f.write(f"{'='*80}\n\n")
    
    try:
        with open(results_summary, 'r', encoding='utf-8') as infile:
            f.write(f"\n\n### File: compute_benefit_summary.md\n\n```markdown\n")
            f.write(infile.read())
            f.write("\n```\n")
    except Exception as e:
        pass
    
    for res_file in results_dir.glob('*'):
        if res_file.is_file():
            f.write(f"\n\n### File: {res_file.name}\n\n```\n")
            try:
                with open(res_file, 'r', encoding='utf-8') as infile:
                    f.write(infile.read())
            except Exception as e:
                f.write(f"Error reading file {res_file}: {e}\n")
            f.write("\n```\n")
