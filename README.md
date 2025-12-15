# 🤖 AI Pull Request Generator

Generador automático de Pull Requests (PR) utilizando Inteligencia Artificial (**Llama 3.1**) y análisis de Git.

Esta herramienta analiza tus commits recientes y los archivos modificados para redactar una descripción técnica detallada, profesional y estructurada ("Nivel Arquitecto"), eliminando el trabajo manual de documentar cambios.

## ✨ Características Principales

  * **🧠 IA Avanzada (Local):** Utiliza `llama3.1` vía Ollama para escribir resúmenes narrativos y explicaciones de pruebas.
  * **🕵️‍♂️ Detección Automática de Tecnología:** Identifica si el proyecto es **Laravel, Python, Dolibarr** o Genérico y adapta el contenido.
  * **✅ Checklists Estrictos:** Genera listas de tareas técnicas y de merge basadas en la realidad del código (no alucinaciones de la IA).
  * **📂 Organización Automática:** Guarda los PRs generados en una carpeta organizada por Proyecto y Fecha.
  * **📋 Portapapeles:** Copia automáticamente el contenido generado al portapapeles listo para pegar en GitHub/GitLab.
  * **🧹 Formato Limpio:** Incluye limpieza automática de Markdown para asegurar títulos y listas perfectas.

-----

## 🚀 Requisitos Previos

Antes de usar el script, necesitas tener instalado lo siguiente:

1.  **Python 3.x** instalado.
2.  **Git** inicializado en tu proyecto.
3.  **Ollama** (para correr el modelo de IA localmente).

### 1\. Instalar Ollama y el Modelo

Descarga Ollama desde [ollama.com](https://ollama.com) e instálalo. Luego, descarga el modelo Llama 3.1 (recomendado para este script):

```bash
ollama pull llama3.1
```

### 2\. Instalar Librerías de Python

Este script requiere un par de librerías para la barra de progreso y el manejo del portapapeles:

```bash
pip install tqdm pyperclip
```

-----

## 🛠️ Instalación y Configuración

1.  **Clona este repositorio** en una carpeta de herramientas (ej. `~/Tools/ai-pr-generator`):

    ```bash
    git clone https://github.com/alann-estrada-KSH/ai-pr-generator.git
    cd ai-pr-generator
    ```

2.  **Configura la ruta de salida (Opcional):**
    Por defecto, los PRs se guardan en `~/KSH/Projects`. Puedes cambiar esto editando la línea en el script:

    ```python
    # Busca esta línea en el script y cámbiala a tu gusto
    projects_folder = os.path.join(os.path.expanduser("~"), 'MisDocumentos', 'PRs')
    ```

-----

## 💻 Uso

Navega desde tu terminal a la carpeta de **cualquier proyecto** git y ejecuta el script.

### Sintaxis Básica

```bash
python /ruta/al/script/generate_pr.py [numero_de_commits]
```

  * **`[numero_de_commits]`**: (Opcional) Cuántos commits hacia atrás analizar. Por defecto es `1`.

### Ejemplo Práctico

Estás trabajando en un proyecto Laravel y quieres generar un PR de tus últimos 5 commits:

```bash
# Estando en la carpeta de tu proyecto Laravel
python ~/Tools/ai-pr-generator/generate_pr.py 5
```

1.  El script te preguntará si quieres agregar **Referencias de Tareas** (Jira, Trello, etc.).
2.  Analizará los archivos y commits.
3.  La IA redactará el contenido.
4.  **¡Listo\!** El PR se guardará en un archivo `.md` y se copiará a tu portapapeles.

-----

## ⚡ Tip Pro: Crear un Alias

Para no escribir la ruta completa del script cada vez, crea un alias en tu terminal.

### En Mac/Linux (Zsh/Bash)

Añade esto a tu archivo `.zshrc` o `.bashrc`:

```bash
alias gpr="python3 ~/ruta/donde/guardaste/generate_pr.py"
```

Recarga la configuración (`source ~/.zshrc`) y ahora solo tendrás que escribir:

```bash
gpr 3
```

### En Windows (PowerShell)

Abre tu perfil de PowerShell (`notepad $PROFILE`) y añade:

```powershell
function gpr { python "C:\Ruta\Al\Script\generate_pr.py" $args }
```

-----

## 🎨 Personalización

El script es modular. Puedes editar fácilmente las plantillas en el código:

  * **`TEMPLATE_LARAVEL`, `TEMPLATE_PYTHON`, etc.:** Modifica los checklists técnicos automáticos.
  * **`MERGE_TEMPLATES`:** Modifica los requisitos finales antes de hacer merge (ej. requerir `php artisan test` o `pytest`).

-----

## 📝 Licencia

Este proyecto es de uso libre. ¡Siéntete libre de forkearlo y mejorarlo\!
