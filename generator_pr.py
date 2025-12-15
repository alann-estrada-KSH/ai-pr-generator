import subprocess
import re
import os
import sys
import pyperclip
from tqdm import tqdm
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PLANTILLAS TÉCNICAS ---
TEMPLATE_LARAVEL = [
    "- [ ] Nuevo endpoint en el controlador `PermissionController` (o lógica backend)",
    "- [ ] Modificación de la base de datos (nueva migración)",
    "- [ ] Actualización de pruebas unitarias e integración"
]

TEMPLATE_PYTHON = [
    "- [ ] Cambios en lógica principal (.py)",
    "- [ ] Modificación de dependencias (requirements/pip)",
    "- [ ] Actualización de tests (pytest)"
]

TEMPLATE_DOLIBARR = [
    "- [ ] Cambios en descriptores de módulo o SQL",
    "- [ ] Modificación de lógica PHP/Core",
    "- [ ] Cambios en interfaz (CSS/JS)"
]

# --- 2. CONFIGURACIÓN DE CHECKLISTS DE MERGE ---
MERGE_TEMPLATES = {
    "laravel": """## ✅ Checklist antes de hacer merge
- [x] Código probado localmente
- [ ] Pruebas unitarias pasan (`php artisan test`)
- [ ] Pruebas de integración pasan
- [ ] Revisado por al menos 1 desarrollador""",

    "python": """## ✅ Checklist antes de hacer merge
- [x] Código probado localmente
- [ ] Pruebas unitarias pasan (`pytest`)
- [ ] Linter verificado (`flake8` / `black`)
- [ ] Revisado por al menos 1 desarrollador""",

    "dolibarr": """## ✅ Checklist antes de hacer merge
- [x] Código probado localmente
- [ ] Módulo activado y verificado en entorno de pruebas
- [ ] Scripts SQL ejecutados sin errores
- [ ] Revisado por al menos 1 desarrollador""",

    "generic": """## ✅ Checklist antes de hacer merge
- [x] Código probado localmente
- [ ] Pruebas manuales completadas
- [ ] Documentación actualizada
- [ ] Revisado por al menos 1 desarrollador"""
}

# --- FUNCIONES DE LIMPIEZA AVANZADA (NUEVO) ---

def clean_garbage(text):
    """
    Elimina líneas decorativas basura y arregla espacios extraños.
    """
    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 1. Eliminar líneas que son solo guiones o iguales (ej: ------- o =======)
        # Esto elimina el subrayado feo debajo de los títulos
        if re.match(r'^[-=]{3,}$', stripped):
            continue
            
        # 2. Arreglar listas con muchos espacios (ej: "* Texto" -> "- Texto")
        if re.match(r'^\s*[\*]\s{2,}', line):
            line = re.sub(r'^\s*[\*]\s+', '- ', line)
            
        cleaned_lines.append(line)
        
    text = "\n".join(cleaned_lines)
    
    # 3. Eliminar exceso de saltos de línea (más de 2 seguidos)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def repair_headers(text):
    """
    Fuerza el formato correcto de los títulos ignorando variaciones de la IA.
    """
    replacements = {
        r"(?i)^(\*\*|#|##)?\s*Resumen del cambio.*": "## 📌 Resumen del cambio",
        r"(?i)^(\*\*|#|##)?\s*¿?Qu[ée] problema soluciona\?.*": "## 🔍 ¿Qué problema soluciona?",
        r"(?i)^(\*\*|#|##)?\s*¿?C[óo]mo probarlo\?.*": "## 🚀 ¿Cómo probarlo?",
        r"(?i)^(\*\*|#|##)?\s*Consideraciones adicionales.*": "## ⚠️ Consideraciones adicionales",
    }
    
    cleaned_lines = []
    for line in text.splitlines():
        replaced = False
        for pattern, replacement in replacements.items():
            if re.match(pattern, line.strip()):
                cleaned_lines.append("\n" + replacement)
                replaced = True
                break
        if not replaced:
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines).strip()

# --- LÓGICA TÉCNICA Y DETECCIÓN ---

def get_marked_checklist(project_type, stats_output):
    stats = stats_output.lower()
    checklist = []
    
    if project_type == "laravel":
        checklist = list(TEMPLATE_LARAVEL)
        if any(x in stats for x in ["controller", "route", "api.php", "web.php", "trait", "service", "request"]):
            checklist[0] = checklist[0].replace("[ ]", "[x]")
        if any(x in stats for x in ["migration", "schema", "model", "database", "pivot"]):
            checklist[1] = checklist[1].replace("[ ]", "[x]")
        if "test" in stats or "phpunit" in stats:
            checklist[2] = checklist[2].replace("[ ]", "[x]")

    elif project_type == "python":
        checklist = list(TEMPLATE_PYTHON)
        if ".py" in stats: checklist[0] = checklist[0].replace("[ ]", "[x]")
        if "requirements" in stats or ".toml" in stats: checklist[1] = checklist[1].replace("[ ]", "[x]")
        if "test" in stats: checklist[2] = checklist[2].replace("[ ]", "[x]")

    elif project_type == "dolibarr":
        checklist = list(TEMPLATE_DOLIBARR)
        if "sql" in stats or "descriptor" in stats: checklist[0] = checklist[0].replace("[ ]", "[x]")
        if ".php" in stats: checklist[1] = checklist[1].replace("[ ]", "[x]")
        if ".css" in stats or ".js" in stats: checklist[2] = checklist[2].replace("[ ]", "[x]")
    
    else:
        checklist = ["- [ ] Revisión manual de cambios genéricos"]

    return "\n".join(checklist)

def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8', errors='replace')
    return result.stdout.strip()

def detect_project_type():
    files = os.listdir('.')
    if 'artisan' in files: return 'laravel'
    if 'main.inc.php' in files: return 'dolibarr'
    if 'requirements.txt' in files or 'pyproject.toml' in files: return 'python'
    return 'generic'

def get_git_info(num_commits):
    logs = run_command(f'git log -n {num_commits} --pretty=format:"Commit: %s%nDesc: %b%n"')
    stats = run_command(f'git diff --stat HEAD~{num_commits} HEAD')
    return logs, stats

def get_tasks_input():
    try:
        num = input("\n ¿Cuántas tareas son? (Enter para 0): ")
        if not num.strip(): return []
        return [input(f" Tarea {i+1}: ") for i in range(int(num))]
    except: return []

# --- PROMPT ACTUALIZADO ---

def build_prompt(logs, stats, project_type, branch_name):
    return f"""
Actúa como un TECH LEAD / ARQUITECTO DE SOFTWARE experto en {project_type}.
Tu tarea es escribir la documentación técnica de este PR.

DATOS:
- Rama: {branch_name}
- Archivos Modificados:
{stats}
- Mensajes de Commit:
{logs}

INSTRUCCIONES DE FORMATO (ESTRICTO):
1. NO escribas saludos ni introducciones.
2. NO uses subrayados ni líneas de separación (ej: "---") debajo de los títulos.
3. NO generes checkboxes, ni listas de cambios, ni checklists. Solo texto narrativo.
4. Usa listas Markdown estándar con guiones ("- Item").

ESTRUCTURA Y CONTENIDO REQUERIDO:

## Resumen del cambio
(Escribe al menos 5 párrafos detallados. Menciona nombres de archivos técnicos importantes como Controllers, Traits, Pivots. Explica la arquitectura y relaciones de datos si aplica).

## ¿Qué problema soluciona?
(Enfócate en el valor técnico y de negocio).

## ¿Cómo probarlo?
1. Cambia a la rama `{branch_name}`.
(Lista los pasos numerados. Si incluyes código, usa bloques markdown estándar ```bash. Si hay migraciones, pon el comando exacto. Sugiere rutas URL basadas en los controladores modificados).

## Consideraciones adicionales
(Menciona comandos extra si son necesarios como npm run build, composer install, actualizaciones de BD, permisos o riesgos de seguridad. Si no, pon "Ninguna").
"""

def run_ollama(prompt):
    print("\n 🧠 Analizando a profundidad con Llama 3.1...")
    res = subprocess.run(['ollama', 'run', 'llama3.1'], input=prompt.encode(), capture_output=True)
    if res.returncode != 0: sys.exit(1)
    return res.stdout.decode('utf-8', errors='replace')

# --- MAIN ---

def main():
    num_commits = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    project_type = detect_project_type()
    print(f"\n 🔎 Proyecto detectado: \033[1m{project_type.upper()}\033[0m")
    
    tasks = get_tasks_input()
    
    with tqdm(total=100, desc="Generando PR", ncols=100) as pbar:
        logs, stats = get_git_info(num_commits)
        branch = run_command('git rev-parse --abbrev-ref HEAD')
        last_commit = run_command('git rev-parse HEAD')
        pbar.update(20)
        
        # 1. Checklist Técnico (Python)
        technical_checklist = get_marked_checklist(project_type, stats)
        
        # 2. Generación IA
        prompt = build_prompt(logs, stats, project_type, branch)
        ai_raw_content = run_ollama(prompt)
        pbar.update(50)
        
        # 3. Limpieza y Reparación
        # Primero quitamos basura visual
        content_clean = clean_garbage(ai_raw_content)
        # Luego forzamos los encabezados bonitos
        content_fixed = repair_headers(content_clean)
        
        # Limpieza de alucinaciones (IA intentando hacer checkboxes)
        content_fixed = re.sub(r'##.*Cambios realizados[\s\S]*', '', content_fixed, flags=re.IGNORECASE)
        content_fixed = re.sub(r'##.*Checklist[\s\S]*', '', content_fixed, flags=re.IGNORECASE)
        
        # 4. Inserción de Bloques Finales
        
        # Tareas
        if tasks:
            task_section = "## 🗂️ Referencias de tareas\n" + "\n".join([f"- {t}" for t in tasks])
            if "## 🔍" in content_fixed:
                content_fixed = content_fixed.replace("## 🔍", f"{task_section}\n\n## 🔍")
            else:
                content_fixed += f"\n\n{task_section}"

        # Checklist Técnico (El de "Cambios Realizados")
        final_pr = content_fixed.strip()
        final_pr += "\n\n## 🛠️ Cambios realizados\n"
        final_pr += technical_checklist
        
        # Checklist de Merge (El dinámico del final)
        final_pr += "\n\n" + MERGE_TEMPLATES.get(project_type, MERGE_TEMPLATES["generic"])
        
        pbar.update(30)

    # Guardado
    projects_folder = os.path.join(os.path.expanduser("~"), 'KSH', 'Projects')
    project_name = os.path.basename(os.getcwd())
    pr_folder = os.path.join(projects_folder, f"{project_name} - PR", datetime.now().strftime("%d-%m-%Y"))
    if not os.path.exists(pr_folder): os.makedirs(pr_folder)
    
    file_path = os.path.join(pr_folder, f"PR_{last_commit[:7]}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_pr)
        
    try: pyperclip.copy(final_pr)
    except: pass
    
    print(f"\n ✅ PR generado en: {file_path}")

if __name__ == "__main__":
    main()
