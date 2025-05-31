import os
import subprocess
from collections import defaultdict     # tipo de diccionario que permite valor default para claves que no existen
from datetime import datetime
import nbformat
from nbconvert.preprocessors import ClearOutputPreprocessor
from enum import Enum

class SubmissionStatus(Enum):
    ON_TIME = 1
    LATE = 2
    MISSING = 3
    UNTRACKED = 4
    DUPLICATED = 5

def get_git_commit_data(repo_path):
    """Gets the commit data from a Git repository."""
    try:
        # Navigate to the repository and fetch commit logs
        commit_logs = subprocess.check_output(
            ["git", "log", "--date=short", "--pretty=format:%ad"],
            cwd=repo_path,
            text=True,
        )
        return commit_logs.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error accessing Git repository at {repo_path}: {e}")
        return []

def summarize_commits_by_month(commit_dates):
    """Summarizes the commits by month."""
    summary = defaultdict(int)      # cualquier clave que no exista se inicializa a 0
    for date_str in commit_dates:
        try:
            # Parse the date and format as YYYY-MM
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = date.strftime("%Y-%m")
            summary[month_key] += 1
        except ValueError:
            print(f"Invalid date format: {date_str}")
    return summary  # diccionario en el que cada clave es un mes y los valores son el numero de commits (0 si no hay en ese mes)

def get_git_commit_date_for_file(repo_path, filename):
    """
    Get the latest commit date for a given file using git log.

    Args:
        filename (str): The path to the file for which to find the latest commit date.
        repo_path (str): The path to the git repository.

    Returns:
        str: The latest commit date in 'YYYY-MM-DD' format, or None if the file is not in git or has no commits.
    """
    try:
        # Build the git command
        command = ["git", "-C", repo_path, "log", "-1", "--pretty=format:%ad", "--date=short", filename]
        
        # # Show the command being executed
        # print(f"Executing command: {' '.join(command)}")
        
        # Run git log to get the latest commit date for the file
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        # Return the latest commit date
        return result.stdout.strip() if result.stdout else None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")
        return None


def find_repositories(base_dir):
    """Finds all repositories in the user subdirectories."""
    repo_dirs = []

    for user_dir in os.listdir(base_dir):
        # construir ruta completa con la carpeta de usuario
        user_path = os.path.join(base_dir, user_dir)

        # comprobar que es un directorio que empieza por "jupyter-" (los usuarios de los alumnos empiezan así)
        if os.path.isdir(user_path) and user_dir.startswith("jupyter-"):

            # añade a la ruta "fc-alumno" y comprueba que es un directorio
            repo_path = os.path.join(user_path, "fc-alumno")
            if os.path.isdir(repo_path):
                repo_dirs.append(repo_path)
    
    # Devuelve la lista con el repositorio de todos los alumnos
    return repo_dirs

def extract_user_identity(repo_path):
    """Extracts the user's name and email from the repository."""
    try:
        # ejecutar git log
        user_info = subprocess.check_output(
            ["git", "log", "--max-count=1", "--pretty=format:%an %ae"],
            cwd=repo_path,
            text=True,
        )
        # rsplit divide por espacios una vez (parámetro 1) empezando por la derecha
        name, email = user_info.rsplit(" ", 1)
        return name, email
    except subprocess.CalledProcessError as e:
        print(f"Error extracting user identity from {repo_path}: {e}")
        return None, None

def check_commit_deadline_for_file(repo_path, filename, date):
    """
    Check if the latest commit date for a file meets the given deadline.

    Args:
        date (str): The deadline date in 'YYYY-MM-DD' format.
        repo_path (str): The path to the git repository.
        filename (str): The path to the file to check.

    Returns:
        int: Number from 1 to 5 indicating whether the file is untracked, on time xor late.
    """
    commit_date = get_git_commit_date_for_file(repo_path, filename)
    if not commit_date:
        # print(f"No commit history found for {filename}, or the file is not tracked by git.")
        return SubmissionStatus.UNTRACKED

    if commit_date <= date:
        #print(f"The file {filename} meets the deadline: {commit_date} <= {date}.")
        return SubmissionStatus.ON_TIME
    else:
        #print(f"The file {filename} does not meet the deadline: {commit_date} > {date}.")
        return SubmissionStatus.LATE

def locate_file_in_repo(repo_path, filename):
    """
    Locate a file in the repository, ignoring directories named "outputs".

    Args:
        repo_path (str): The path to the git repository.
        filename (str): The name of the file to locate.

    Returns:
        str: The relative path to the file within the repository, or None if not found.
    """
    file_paths = []
    for root, dirs, files in os.walk(repo_path):
        # Skip directories named "outputs"
        dirs[:] = [d for d in dirs if d not in ["outputs", ".git", ".ipynb_checkpoints"]]
        if filename in files:
            file_paths.append(os.path.relpath(os.path.join(root, filename), repo_path))

    return file_paths

def locate_relevant_files(repo_path, relevant_files):
    """
    Return a dictionary in which each relevant file is mapped to its route in the repository.
    """
    filepaths = {}
    for filename in relevant_files:
        filepaths[filename]=locate_file_in_repo(repo_path, filename)
    return filepaths
                                      
def check_deadlines(repo_path, file_deadlines, filepaths):
    """
    Check if multiple files meet their respective deadlines.

    Args:
        repo_path (str): The path to the git repository.
        file_deadlines (list of tuples): A list of tuples where each tuple contains:
            - filename (str): The path to the file.
            - deadline (str): The deadline date in 'YYYY-MM-DD' format.
        filepaths (dict): paths to relevant files in the repository

    Returns:
        dict: A dictionary where every file in file_deadlines is mapped to a number from 1 to 5 indicating its status.
    """
    results = {}
    for filename, deadline in file_deadlines:
        if len(filepaths[filename]) == 1:
            results[filename]=check_commit_deadline_for_file(repo_path, filepaths[filename][0], deadline)
        elif len(filepaths[filename]) > 1:
            # print(f"Error: {filename} appears to be duplicated!")
            results[filename]=SubmissionStatus.DUPLICATED
        else:
            # print(f"Error: {filename} not found!")
            results[filename]=SubmissionStatus.MISSING
    return results

import hashlib

def compute_file_checksum(file_path):
    """Compute the SHA-256 checksum of a file."""
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):  # Read the file in chunks
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error computing checksum for {file_path}: {e}")
        return None

def detect_plagiarism(user_data):
    """
    Detect plagiarism by finding users with the same file checksums. 

    El parámetro de entrada user_data es un diccionario con los email como claves, y sus valores son diccionarios con:
        - nombre del alumno
        - ruta a su repositorio
        - diccionario de rutas a ficheros de interés
        - diccionario de ruta_archivo:checksum
        - diccionario de número de commits por meses
        - diccionario con el estado de cada archivo
    """
    # Create a mapping of filename to a dictionary of {checksum: [users]}
    plagiarism_map = defaultdict(lambda: defaultdict(list))

    # plagiarism_map es un diccionario en el que las claves son el nombre del archivo, y los valores son diccionarios 
    # cuyas claves son el checksum del archivo, y el valor es una lista de usuarios con dicho checksum

    for email, data in user_data.items():
        for filename, checksum in data.get("checksums", {}).items():
            plagiarism_map[filename][checksum].append(email)

    # Print cases where multiple users share the same checksum for a file
    print("\nPlagiarism Detection Results:")
    # Recorrer archivos
    for filename, checksums in plagiarism_map.items():
        # Recorrer la lista de usuarios para cada checksum
        for checksum, users in checksums.items():
            if len(users) > 1:
                print(f"  Filename: {filename}")
                print(f"    Checksum: {checksum}")
                print(f"    Users: {', '.join(users)}")


def analyze_repositories(base_dir, file_deadlines):
    """
    Analyzes a list of repositories and summarizes commit progress and deadlines.

    Args:
        base_dir (str): The path to the directory where the different repositories are allocated.
        file_deadlines (list of tuples): A list of tuples where each tuple contains:
            - filename (str): The path to the file.
            - deadline (str): The deadline date in 'YYYY-MM-DD' format.
    """

    # Encontrar rutas de repositorios a analizar a partir de base_dir 
    repo_dirs = find_repositories(base_dir)
    relevant_filenames = [t[0] for t in file_deadlines]
    user_data = {}

    for repo_dir in repo_dirs:
        # Comprobar que el directorio dado para el repositorio es válido
        if not os.path.isdir(repo_dir):
            print(f"Invalid directory: {repo_dir}")
            continue

        print(f"Analyzing repository: {repo_dir}")

        # Extraer información del usuario cuyo repositorio analizamos
        name, email = extract_user_identity(repo_dir)
        if not email:
            print(f"Could not extract user identity for repository: {repo_dir}")
            continue
        
        # Extraer fechas de sus commits y organizarlas por mes
        commit_dates = get_git_commit_data(repo_dir)
        if commit_dates:
            # diccionario en el que las claves son meses y los valores son número de commits/mes
            commits_by_month = summarize_commits_by_month(commit_dates)

        # Localizar en el repositorio los archivos que nos interesan (por su nombre)
        file_paths = locate_relevant_files(repo_dir, relevant_filenames)

        # Clear outputs before computing checksums
        clear_notebook_output(repo_dir, file_paths)

        # Para todos los archivos que nos interesan, calcular su checksum (buscar el archivo en el directorio y calcularlo)
        file_checksums = {}     # nombre_archivo:checksum
        for file, path in file_paths.items():
            if len(path) == 1:
                file_checksums[file] = compute_file_checksum(os.path.join(repo_dir,path[0]))

        # Obtener diccionario que mapea el nombre del archivo con su estado (1-5) en base al último commit  
        deadline_results = check_deadlines(repo_dir, file_deadlines, file_paths)

        # Mapear al email del alumno los resultados del análisis
        user_data[email] = {
            "name": name,
            "repo_path": repo_dir,
            "file_paths" : file_paths,
            "checksums" : file_checksums,
            "repo_summary": commits_by_month,
            "deadlines": deadline_results,
        }

    return user_data


def clear_notebook_output(repo_dir, file_paths):
    """
    Clears the output of all cells in the provided notebook files.

    Args:
        file_paths (list): List of notebook file paths to process.
    """
    for file, paths in file_paths.items():
        if len(paths) == 1:
            file_path = os.path.join(repo_dir, paths[0])
            if file_path.endswith('.ipynb'):
                try:
                    # Read the notebook
                    with open(file_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                    
                    # Clear the outputs
                    ClearOutputPreprocessor().preprocess(nb, {})
                    
                    # Save the cleared notebook
                    with open(file_path, 'w', encoding='utf-8') as f:
                        nbformat.write(nb, f)
                    
                    #print(f"Cleared output for notebook: {file_path}")
                except Exception as e:
                    print(f"Error processing notebook {file_path}: {e}")

def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python script.py <base_directory>")
    #     sys.exit(1)

    # Base directory containing user subdirectories
    # base_dir = sys.argv[1]
    base_dir = os.path.join(os.getcwd(),"repos")

    # Example list of file deadlines
    file_deadlines = [
        ("practica1-introshell-ejercicios.ipynb", "2024-09-27"),
        ("practica2-introgit-ejercicios.ipynb", "2024-10-14"),
        ("practica3-okteta-enteros-reales-ejercicios.ipynb", "2024-10-28"),
        ("practica4a-compilacion-ejecucion-ejercicios.ipynb", "2024-11-04"),
        ("practica5a-ficheros-ejercicios.ipynb", "2024-11-18"),
        ("practica5b-busquedas-ejercicios.ipynb", "2024-11-18"),
        ("practica6a-cache-boletin.ipynb", "2024-11-25"),
        ("practica7a-procesos-ejercicios.ipynb", "2024-12-09"),
        ("practica7b-tuberias-ejercicios.ipynb", "2024-12-09"),
    ]

    # Analyze repositories and print summary
    user_summaries = analyze_repositories(base_dir, file_deadlines)

    # Sort the user summaries by the 'name' attribute
    sorted_summaries = sorted(user_summaries.items(), key=lambda item: item[1]['name'])

    print("\nUser Repository Summaries:")
    for email, data in sorted_summaries:
        print(f"\nEmail: {email}")
        print(f"  Name: {data['name']}")
        print(f"  Repository Summary: {data['repo_path']}")
        for month, count in sorted(data['repo_summary'].items()):
            print(f"    {month}: {count} commits")
        print(f"  Deadline Check:")
        for file, status in data['deadlines'].items():
            print(f"    {file}: {status.name}")

    # Detect plagiarism
    detect_plagiarism(user_summaries)

if __name__ == "__main__":
    main()
