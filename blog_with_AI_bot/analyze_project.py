# analyze_project.py

# parse_project_fulltext.py
import os
import json

EXCLUDE_DIRS = {
    "__pycache__", ".git", "venv", "env", ".idea",
    ".vscode", "migrations", "node_modules", "__init__.py"
}

INCLUDE_EXTS = (".py", ".html", ".js", ".css", ".json", ".md")

def collect_files(root: str) -> list[dict[str, str]]:
    """Рекурсивно проходит проект и сохраняет полный текст всех подходящих файлов."""
    dataset = []

    for dirpath, dirnames, filenames in os.walk(root):
        # отфильтровываем системные папки
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if filename.endswith(INCLUDE_EXTS):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception as e:
                    content = f"⚠️ [READ ERROR: {e}]"

                dataset.append({
                    "path": filepath,
                    "name": filename,
                    "extension": os.path.splitext(filename)[1],
                    "content": content
                })
    return dataset


def save_as_json(dataset: list[dict[str, str]], out_file: str = "project_fulltext.json"):
    """Сохраняет весь собранный код в JSON"""
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(dataset)} файлов → {out_file}")


if __name__ == "__main__":
    root_dir = "."  # можно заменить на путь проекта
    data = collect_files(root_dir)
    save_as_json(data, "project_fulltext.json")
