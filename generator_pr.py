import subprocess
import re
import os
import sys
import pyperclip
from tqdm import tqdm

# Función para ejecutar comandos
def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error ejecutando '{cmd}':\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

# Función para obtener el log de Git
def get_git_log(num_commits):
    return run_command(f'git log -n {num_commits} --pretty=format:"- %s%n  %b%n"')

# Función para obtener el último commit (ID)
def get_last_commit_id():
    return run_command('git rev-parse HEAD')

# Función para construir el prompt para LLaMA
def build_prompt(num_commits, git_log):
    return f"""A continuación te doy el resumen de los últimos {num_commits} commit(s) de Git. Usá esa información para rellenar los campos necesarios de esta plantilla de Pull Request en español. NO cambies la estructura ni los emojis. NO expliques lo que hacés. Solo completá los campos. Mantené el formato utf-8, tambien, elimina los comentarios de <!-- -->, esos solamente son de guia. Sé detallado: escribí oraciones completas, brindá contexto, y describí con claridad los cambios hechos, los problemas que resuelve y cómo probarlo. No seas breve.

Resumen de commits:
{git_log}

Plantilla:

## Resumen del cambio
<!-- Explica brevemente qué cambios se realizaron y por qué. -->

## ¿Qué problema soluciona?
<!-- Especifica el problema o feature relacionado. Si hay un issue en GitHub, enlázalo: (agregalo segun se requiera)-->

## ¿Cómo probarlo?
<!-- Describe los pasos para probar el cambio (según se aplique)-->

## Cambios realizados
<!-- Marca con x los cambios incluidos en este PR, Asegurate de mantener los tres ítems del checklist, incluso si no aplican -->
- [ ] Nuevo endpoint en el controlador `PermissionController`
- [ ] Modificación de la base de datos (nueva migración)
- [ ] Actualización de pruebas unitarias e integración

## x Consideraciones adicionales
<!-- ¿Este PR tiene efectos colaterales? ¿Requiere migraciones o configuración extra? (según se aplique) -->

## Checklist antes de hacer merge
<!-- Asegurate de mantener los cuatro ítems del checklist, incluso si no aplican -->
- [x] Código probado localmente
- [ ] Pruebas unitarias pasan (`php artisan test`)
- [ ] Pruebas de integración pasan
- [ ] Revisado por al menos 1 desarrollador
"""

# Función para ejecutar Ollama
def run_ollama(prompt):
    result = subprocess.run(
        ['ollama', 'run', 'mistral'],
        input=prompt.encode('utf-8'),     # 👉 codificamos el prompt
        capture_output=True               # salida como bytes
    )
    if result.returncode != 0:
        print("❌ Error ejecutando ollama:\n")
        print(result.stderr.decode('utf-8', errors='replace'))
        sys.exit(1)
    return result.stdout.decode('utf-8', errors='replace') 

# Función para corregir los encabezados del PR
def fix_headers(text):
    replacements = {
        r"## Resumen del cambio": "## 📌 Resumen del cambio",
        r"## ¿Qué problema soluciona\?": "## 🔍 ¿Qué problema soluciona?",
        r"## ¿Cómo probarlo\?": "## 🚀 ¿Cómo probarlo?",
        r"## Cambios realizados": "## 🛠️ Cambios realizados",
        r"## Consideraciones adicionales": "## ⚠️ Consideraciones adicionales",
        r"## Checklist antes de hacer merge": "## ✅ Checklist antes de hacer merge",
        r"## ?Resumen del cambio": "## 📌 Resumen del cambio",  # fallback si no tiene signos raros
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    return text

# Función principal
def main():
    # Obtener el número de commits (por defecto es 1)
    num_commits = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    # Obtener el log de git
    git_log = get_git_log(num_commits)

    # Obtener el commit ID
    last_commit_id = get_last_commit_id()

    # Construir el prompt
    prompt = build_prompt(num_commits, git_log)

    # Ejecutar Ollama para obtener el resultado
    print("🧠 Procesando con Ollama...")
    result_text = run_ollama(prompt)

    # Corregir los encabezados
    result_text = fix_headers(result_text)

    # Crear carpeta de PRs fuera del proyecto (en 'projects')
    projects_folder = os.path.join(os.path.expanduser("~"), 'KSH', 'Projects')
    project_name = os.path.basename(os.getcwd())  # Obtiene el nombre del proyecto
    pr_folder = os.path.join(projects_folder, f"{project_name} - PR")

    if not os.path.exists(pr_folder):
        os.makedirs(pr_folder)

    # Nombre del archivo PR con el ID del commit
    pr_file_name = f"PULL_REQUEST_{last_commit_id}.md"
    file_path = os.path.join(pr_folder, pr_file_name)

    # Guardar el archivo
    with open(file_path, "w", encoding="utf-8", errors='replace') as f:
        f.write(result_text)

    # Copiar al portapapeles
    try:
        pyperclip.copy(result_text)
        print("📋 Copiado al portapapeles.")
    except pyperclip.PyperclipException:
        print("⚠️ No se pudo copiar al portapapeles. ¿Estás en un entorno sin GUI?")

    # Confirmación final
    print(f"✅ Pull Request generado y guardado en: {file_path}")

if __name__ == "__main__":
    # Agregar barra de progreso para el proceso
    with tqdm(total=100, desc="Generando PR", ncols=100) as pbar:
        main()
        pbar.update(100)  # Marca como completo
