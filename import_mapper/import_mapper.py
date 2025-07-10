import argparse
from import_mapper.core.mapper import ImportMapper

def main():
    parser = argparse.ArgumentParser(description="Python import dependency analyzer.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project folder path to scan.")
    parser.add_argument("--output", default="dependency_map.json", help="Output JSON file.")
    parser.add_argument("--detailed", action="store_true", help="Enable detailed import analysis.")
    args = parser.parse_args()

    mapper = ImportMapper(args.project_path, detailed=args.detailed)
    result = mapper.run_analysis()
    mapper.save_to_json(result, args.output)

if __name__ == "__main__":
    main()
