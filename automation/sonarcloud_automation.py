import os
import requests
from pathlib import Path

# =====================================
# CONFIG
# =====================================

SONAR_TOKEN = os.getenv("SONAR_TOKEN")

ORGANIZATION = "pipeline-jenkins"

SONARCLOUD_URL = "https://sonarcloud.io"

# =====================================
# DETECTAR LENGUAJE
# =====================================

def detect_language(project_path):

    extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.php': 'php',
        '.go': 'go',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rb': 'ruby'
    }

    counter = {}

    for root, _, files in os.walk(project_path):

        for file in files:

            ext = Path(file).suffix

            if ext in extensions:

                lang = extensions[ext]

                counter[lang] = counter.get(lang, 0) + 1

    if not counter:
        return "unknown"

    return max(counter, key=counter.get)

# =====================================
# CREAR PROYECTO SONARCLOUD
# =====================================

def create_project(project_key, project_name):

    url = f"{SONARCLOUD_URL}/api/projects/create"

    data = {
        "organization": ORGANIZATION,
        "project": project_key,
        "name": project_name
    }

    response = requests.post(
        url,
        auth=(SONAR_TOKEN, ""),
        data=data
    )

    if response.status_code == 200:

        print(f"[+] Proyecto creado: {project_name}")

    elif "already exists" in response.text.lower():

        print(f"[!] El proyecto ya existe: {project_name}")

    else:

        print("[!] Error creando proyecto:")
        print(response.text)

# =====================================
# GENERAR CONFIG
# =====================================

def generate_properties(project_path, project_key, project_name):

    content = f"""
sonar.projectKey={project_key}
sonar.organization={ORGANIZATION}
sonar.projectName={project_name}
sonar.sources=.
sonar.host.url=https://sonarcloud.io
"""

    properties_file = os.path.join(
        project_path,
        "sonar-project.properties"
    )

    with open(properties_file, "w") as f:
        f.write(content)

    print("[+] sonar-project.properties generado")

# =====================================
# MAIN
# =====================================

def main():

    # Nombre lógico del proyecto
    project_name = os.getenv("PROJECT_NAME")
    
    if not project_name:

        print("[!] PROJECT_NAME no definido")
        return

    # El repo entero es el proyecto vulnerable
    project_path = "."

    if not os.path.exists(project_path):

        print("[!] Proyecto no encontrado")
        return

    # Key dinámica SonarCloud
    project_key = (
        f"pipeline-jenkins_{project_name}"
        .replace(" ", "-")
        .lower()
    )

    language = detect_language(project_path)

    print(f"[+] Proyecto: {project_name}")

    print(f"[+] Lenguaje detectado: {language}")

    create_project(project_key, project_name)

    generate_properties(
        project_path,
        project_key,
        project_name
    )

    print("\n[+] Configuración finalizada")

    print(
        f"https://sonarcloud.io/project/overview?id={project_key}"
    )

if __name__ == "__main__":
    main()
