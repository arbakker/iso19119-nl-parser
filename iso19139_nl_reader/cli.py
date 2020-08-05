import argparse
import json
from .service_record import ServiceRecord
import click

@click.group()
def cli():
    pass


@cli.command(name="read")
@click.argument('md-file', type=click.Path(exists=True))
def read_metadata_command(md_file):
    service_record = ServiceRecord(md_file)
    result = service_record.convert_to_dictionary()
    print(json.dumps(result, indent=4))

@cli.command(name="validate")
@click.argument('md-file', type=click.Path(exists=True))
def validate_metadata_command(md_file):
    service_record = ServiceRecord(md_file)
    result = service_record.schema_validation_errors()
    if result:
        print(result)
        exit(1)
    else:
        print("metadata record is valid")


if __name__ == "__main__":
    cli()
