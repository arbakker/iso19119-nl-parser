import argparse
import json
from .service_record import ServiceRecord

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    args = parser.parse_args()
    md_file_path = args.md_file
    service_record = ServiceRecord(md_file_path)
    result = service_record.convert_to_dictionary()
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
