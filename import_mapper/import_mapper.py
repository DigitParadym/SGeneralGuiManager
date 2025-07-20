import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from import_mapper.core.mapper import ImportMapper

def main():
    parser = argparse.ArgumentParser(description="Analyze Python dependencies.")
    parser.add_argument("project_path", nargs="?", default=".", help="Path to project.")
    parser.add_argument("--output", default="dependency_map.json", help="Output JSON filename.")
    parser.add_argument("--detailed", action="store_true", help="Enable detailed analysis.")
    args = parser.parse_args()

    print("--- Starting dependency analyzer ---")
    mapper = ImportMapper(args.project_path, detailed=args.detailed)
    result = mapper.run_analysis()
    mapper.save_to_json(result, args.output)
    print("--- Analysis completed ---")

if __name__ == "__main__":
    main()
