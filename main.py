import os
import json
from datetime import datetime
from pathlib import Path


class ProjectDocumentationGenerator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_file_info(self, filepath):
        """Получение информации о файле"""
        stat = os.stat(filepath)
        return {
            "path": str(filepath),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": filepath.suffix.lower(),
        }

    def read_file_safe(self, filepath, max_size=1000000):  # 1MB limit
        """Безопасное чтение файла с ограничением размера"""
        try:
            file_size = os.path.getsize(filepath)
            if file_size > max_size:
                return (
                    f"[FILE TOO LARGE: {file_size} bytes, truncated to {max_size}]\n"
                    + self._read_first_lines(filepath, 1000)
                )

            # Пробуем разные кодировки
            encodings = ["utf-8", "latin-1", "cp1251"]
            for encoding in encodings:
                try:
                    with open(filepath, "r", encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue

            return f"[BINARY FILE: {file_size} bytes]"
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    def _read_first_lines(self, filepath, lines=100):
        """Чтение первых N строк файла"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return "".join([next(f) for _ in range(lines)])
        except:
            return "[CANNOT READ FILE CONTENT]"

    def generate_by_category(self):
        """Генерация отдельных файлов по категориям"""
        categories = {
            "python": [".py"],
            "html": [".html"],
            "css": [".css"],
            "javascript": [".js"],
            "config": [".yml", ".yaml", ".ini", ".txt", ".json"],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "sql": [".sql"],
            "markdown": [".md"],
            "other": [],  # Все остальные файлы
        }

        output_dir = f"documentation_{self.timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        # Собираем все файлы
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Пропускаем служебные директории
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.endswith(".pyc"):
                    continue

                filepath = Path(root) / file
                rel_path = filepath.relative_to(self.project_root)

                file_info = {
                    "path": str(rel_path),
                    "full_path": str(filepath),
                    "category": "other",
                }

                # Определяем категорию
                for category, extensions in categories.items():
                    if category == "docker":
                        if file in extensions:
                            file_info["category"] = category
                            break
                    elif any(str(rel_path).endswith(ext) for ext in extensions):
                        file_info["category"] = category
                        break

                all_files.append(file_info)

        # Генерируем файлы по категориям
        for category in categories.keys():
            category_files = [f for f in all_files if f["category"] == category]

            if category_files:
                output_file = Path(output_dir) / f"{category}_files.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"{'='*60}\n")
                    f.write(f"ФАЙЛЫ КАТЕГОРИИ: {category.upper()}\n")
                    f.write(f"{'='*60}\n\n")

                    for file_info in category_files:
                        f.write(f"\n{'▬'*60}\n")
                        f.write(f"📄 ФАЙЛ: {file_info['path']}\n")
                        f.write(f"{'▬'*60}\n\n")

                        content = self.read_file_safe(file_info["full_path"])
                        f.write(content)
                        f.write("\n\n")

        # Создаем индексный файл
        self._create_index_file(output_dir, all_files, categories)

        print(f"✅ Документация создана в директории: {output_dir}")

    def _create_index_file(self, output_dir, all_files, categories):
        """Создание индексного файла с информацией о проекте"""
        index_file = Path(output_dir) / "PROJECT_INDEX.txt"

        with open(index_file, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("ИНДЕКС ПРОЕКТА ДИПЛОМА\n")
            f.write(f"Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            f.write("📊 СТАТИСТИКА ПО КАТЕГОРИЯМ:\n")
            f.write("-" * 40 + "\n")

            for category in categories.keys():
                count = len([f for f in all_files if f["category"] == category])
                if count > 0:
                    f.write(f"  {category.upper():12}: {count:3d} файлов\n")

            f.write("\n📁 ПОЛНЫЙ СПИСОК ФАЙЛОВ:\n")
            f.write("-" * 40 + "\n")

            for file_info in sorted(all_files, key=lambda x: x["path"]):
                size = os.path.getsize(file_info["full_path"])
                f.write(
                    f"{file_info['path']:60} [{file_info['category']:8}] {size:8,d} bytes\n"
                )

            f.write("\n" + "=" * 70 + "\n")
            f.write("КОНЕЦ ИНДЕКСА\n")
            f.write("=" * 70 + "\n")


def main():
    generator = ProjectDocumentationGenerator()

    print("Выберите формат документации:")
    print("1. Единый файл со всем содержимым")
    print("2. Раздельные файлы по категориям")

    choice = input("Ваш выбор (1 или 2): ").strip()

    if choice == "1":
        # Используем первый скрипт для создания единого файла
        import sys

        sys.path.insert(0, ".")
        exec(open(__file__).read())
    elif choice == "2":
        generator.generate_by_category()
    else:
        print("❌ Неверный выбор. Используется вариант 1 по умолчанию.")
        import sys

        sys.path.insert(0, ".")
        exec(open(__file__).read())


if __name__ == "__main__":
    main()
