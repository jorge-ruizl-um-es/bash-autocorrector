# 🛠️ Bash Autograder  
*Automated Bash Script Correction & Feedback Tool for Jupyter Notebooks*  

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
[![Bash](https://img.shields.io/badge/Bash-5.0%2B-brightgreen)](https://www.gnu.org/software/bash/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)](https://jupyter.org/)

## 🔍 Project Overview

This Python-based tool includes a set of scripts that provides various functionalities for processing Jupyter notebooks. It supports working with notebooks stored in locally cloned git repositories, checking if each file meets the deadline or the existence of any kind of plagiarism. 

In addition, it is focused on giving automated feedback over some notebooks providing a predefined set of solutions. This feedback is far more than a mere correction, as it is able to differentiate between certain states of each solution, evaluating the command and pointing out the kind of mistake in case it exists. 

---

## 📁 Project Structure

```
bash-autocorrector/
│
├── dir_exams/                      
│   └── Example exams for testing the correction and feedback system.  
│
├── entregas_alumnos/              
│   └── Student submissions (repositories) organized for batch correction and logging.  
│
├── practicas/                     
│   └── Practice notebooks with predefined exercises and solutions.  
│
├── pruebas-script-correccion/    
│   └── Output logs and tests used for debugging and validating script corrections.  
│
└── scripts/                       
    ├── correct_exam.py           # Compares answers with solutions and classifies command errors.
    ├── repo-summary.py           # Analyzes student repos to check deadlines and detect plagiarism.
    ├── scores_by_block.py        # Aggregates correction results by block and links answers to scores.
    ├── etiquetar_notebook.py     # Auto-tags notebook cells based on solution templates.
    └── create_csv_correction.py  # Generates CSV summaries from corrected exams.
```

---

## 🔥 Key Features

✅ **Jupyter Notebook Support** - Process `.ipynb` files seamlessly  
✅ **Git Integration** - Works with locally cloned repositories  
✅ **Precise Error Detection** - Identifies specific mistakes in Bash commands  
✅ **Automated Grading** - Compare student scripts against reference solutions  
✅ **Custom feedback generation** - Provides actionable improvement suggestions

---

## 🔬 Detailed Explanation

At the moment, the version of this tool includes a set of scripts located in the folder `scripts`, which we proceed to analyze one by one. The rest of the repository structure consists in the directory `dir_exams` with some notebooks for testing the tool, and the directory `practicas` with practice notebooks.

### `repo-summary.py`

This script is focused on the repositories analysis located in a base directory, each one owned by a student. It checks the format of the assignments by searching the commits related to each one and comparing its date to a provided deadline. 

In order to do this, the script scans the base directory iterating over each repository. It extracts the user information, the path for the relevant file (assignments), the deadline checkup and the checksum (hash SHA-256) after cleaning the notebooks' outputs. This information is stored in a dictionary, which is used for detecting plagiarism.

### `correct_exam.py`

This script integrates the detailed correction of each command in a Jupyter notebook, comparing it to the solutions provided. First, there is a function for reading each notebook of a student, located in a fold, and comparing the answers to the solutions. All these commands are organized in a dictionary with JSON structure. 

Once done that, there is a function to correct each command comparing it to the solution. Depending on the type of command, the correction is lightly different. For example, pipelines, subshells, compound commands, git commands, or `find` commands are corrected each one in the appropriate way. The program set a list of different types of status for each command (BLANK, WRONG_COMMAND, WRONG_SUBSHELL, WRONG_PIPE, WRONG_ARGS, WRONG_OPTIONS, CORRECT). These statuses point out whether the student's command is correct, or what type of mistake has been made.

### `etiquetar_notebook.py`

This script scans all student practice notebooks and automatically tags code cells using the format `#BLOCK.QUESTION`. The tags are extracted from a solution file that includes `#@solution@` markers. This labeling ensures the alignment of exercises between student notebooks and reference solutions, even when students alter the order of exercises.

### `scores_by_block.py`

This module provides a detailed breakdown of each student's responses, organized by blocks. From the raw answers and the official solutions, it builds:
- A dictionary that links each question to its correction status and corresponding commands.
- A mapping of each student's response to the expected answer.
- A count of command error types (`WRONG_ARGS`, `CORRECT`, etc.) per block.

It is used as an internal analysis tool by other scripts that aggregate correction data.

### `create_csv_correction.py`

Generates multiple CSV reports from the automatic correction results. For each student:
- Summarizes the count of each correction status.
- Breaks down scores by block.
- Creates detailed CSVs showing student answers and correction states.

This script automates report generation and supports large-scale evaluation with fine-grained diagnostics.

---

## Credits

This project has been developed by Jorge Ruiz López ([jorge.ruizl@um.es](emailto:jorge.ruizl@um.es)), as part of his academic internship at the Department of Computer Engineering and Technology, Faculty of Computer Science, University of Murcia (Spain). It has academic and educational goals.




