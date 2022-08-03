import os
import argparse

from .models import get_blubber


# Input Rules:
# - When entering version name, reference only the numbers with 2 places.
# - Example: '/v020000' would be referenced as '020000'.


parser = argparse.ArgumentParser()

parser.add_argument("-f", "--func", help = "Create with 'create' and Destroy with 'destroy'.")
parser.add_argument("-v", "--version", help = "Specify which version of database you are building or destroying.")


def _create_tables(version):
    try:
        blubber = get_blubber()

        with blubber.conn.cursor() as cursor:
            cwd = os.getcwd()
            sql_file_path = os.path.join(cwd, f"v{version}/_create.sql")

            with open(sql_file_path, "r") as sql_file:
                cursor.execute(sql_file.read())

    except FileNotFoundError as no_create_sql_present:
        print(no_create_sql_present)

    else:
        print("Successfully created Hubbub database.")

def _destroy_tables(version):
    try:
        blubber = get_blubber()

        with blubber.conn.cursor() as cursor:
            cwd = os.getcwd()
            sql_file_path = os.path.join(cwd, f"v{version}/_destroy.sql")

            with open(sql_file_path, "r") as sql_file:
                cursor.execute(sql_file.read())

    except FileNotFoundError as no_create_sql_present:
        print(no_create_sql_present)

    else:
        print("Successfully destroyed Hubbub database.")



if __name__ == "__main__":
    args = parser.parse_args()

    assert args.func in ["create", "destroy"], "Invalid Blubber CLI operation."

    version = args.version
    
    if args.func == "create": _create_tables(version)
    elif args.func == "destroy": _destroy_tables(version)
