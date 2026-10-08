import argparse
import hashlib
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict


@dataclass
class FileInfo:
    path: str
    sha256: str
    size: int
    mtime: float


def calculate_sha256(file_path: Path) -> str:
    """Обчислює SHA-256 хеш файлу."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (PermissionError, OSError) as e:
        logging.error(f"Не вдалося прочитати файл {file_path}: {e}")
        return ""


def scan_directory(directory: Path) -> Dict[str, FileInfo]:
    """Рекурсивно сканує директорію та повертає словник об'єктів FileInfo."""
    files_data = {}
    for path in directory.rglob("*"):
        # Пропускаємо сам baseline.json та файли логів, щоб уникнути циклів/помилок
        if path.is_file() and path.name not in ["baseline.json", "fim_audit.log"]:
            try:
                rel_path = str(path.relative_to(directory))
                file_stats = path.stat()
                files_data[rel_path] = FileInfo(
                    path=rel_path,
                    sha256=calculate_sha256(path),
                    size=file_stats.st_size,
                    mtime=file_stats.st_mtime,
                )
            except OSError:
                continue
    return files_data


def generate_baseline(directory: Path, baseline_path: Path):
    """Створює еталонний файл baseline.json."""
    data = scan_directory(directory)
    serializable_data = {k: asdict(v) for k, v in data.items()}
    
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(serializable_data, f, indent=4)
    logging.info(f"Baseline створено у {baseline_path}")


def check_integrity(directory: Path, baseline_path: Path):
    """Порівнює поточний стан з baseline.json."""
    if not baseline_path.exists():
        logging.error("Baseline файл не знайдено!")
        return

    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    current_state = scan_directory(directory)
    
    baseline_keys = set(baseline.keys())
    current_keys = set(current_state.keys())

    modified = []
    for key in baseline_keys & current_keys:
        if baseline[key]["sha256"] != current_state[key].sha256:
            modified.append(key)
            logging.warning(f"[MODIFIED] {key}")

    created = current_keys - baseline_keys
    for key in created:
        logging.warning(f"[CREATED] {key}")

    deleted = baseline_keys - current_keys
    for key in deleted:
        logging.warning(f"[DELETED] {key}")

    print(f"\n=== Summary ===")
    print(f"Modified: {len(modified)}, Created: {len(created)}, Deleted: {len(deleted)}")


def main():
    # Налаштування кодування для Windows, щоб уникнути UnicodeEncodeError
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="File Integrity Monitor (FIM)")
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--mode", choices=["generate", "check"], required=True)
    parser.add_argument("--log-file", type=Path, default=Path("labs/lab02/data/fim_audit.log"))
    
    args = parser.parse_args()

    args.log_file.parent.mkdir(parents=True, exist_ok=True)

    # Використовуємо encoding='utf-8' для файлу логів
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(args.log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    if args.mode == "generate":
        generate_baseline(args.dir, args.baseline)
    else:
        check_integrity(args.dir, args.baseline)


if __name__ == "__main__":
    main()