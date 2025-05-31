# 🛠️ Bash Autograder  
*Automated Bash Script Correction & Feedback Tool for Jupyter Notebooks*  

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
[![Bash](https://img.shields.io/badge/Bash-5.0%2B-brightgreen)](https://www.gnu.org/software/bash/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)](https://jupyter.org/)

## 🔍 Project Overview

This Python-based tool includes a set of scripts that provides various functionalities for processing Jupyter notebooks. It supports working with notebooks stored in locally cloned git repositories, checking if each file meets the deadline or the existence of any kind of plagiarism. 

In addition, it is focused on giving automated feedback over some notebooks providing a predefined set of solutions. This feedback is far more than a mere correction, as it is able to differentiate between certain states of each solution, evaluating the command and pointing out the kind of mistake in case it exists. 

### 🔥 Key Features

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


 
