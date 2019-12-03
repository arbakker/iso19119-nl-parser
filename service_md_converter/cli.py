import argparse
import json
from .service_record import ServiceRecord

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    parser.add_argument('--inspire', dest='inspire', action='store_true')
    parser.add_argument('--no-inspire', dest='inspire', action='store_false')
    args = parser.parse_args()
    md_file_path = args.md_file
    inspire = args.inspire
    service_record = ServiceRecord(md_file_path)
    result = service_record.convert_to_dictionary(inspire)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
