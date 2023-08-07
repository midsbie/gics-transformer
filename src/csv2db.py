import argparse
import csv
import sys

import psycopg2


def create_parser():
    parser = argparse.ArgumentParser(
        description="Upsert GICS CSV data into a Postgres database.")

    # Positional arguments
    parser.add_argument('csv_path', type=str,
                        help="Path to the transformed GICS CSV input file.")

    # Mandatory arguments
    parser.add_argument('--db', required=True, type=str,
                        help="Name of the database.")

    # Optional arguments
    parser.add_argument('--username', default='postgres', type=str,
                        help="Username for the database (default: postgres).")
    parser.add_argument('--password', default=None, type=str,
                        help="Password for the database (default: None).")
    parser.add_argument('--host', default='localhost',
                        type=str, help="Database host (default: localhost).")
    parser.add_argument('--port', default=5432, type=int,
                        help="Database port (default: 5432).")

    return parser


def verify_csv_header(reader):
    expected_header = [
        "sector_code", "sector_name",
        "industry_group_code", "industry_group_name",
        "industry_code", "industry_name",
        "sub_industry_code", "sub_industry_name",
        "industry_description"
    ]
    return list(reader.fieldnames) == expected_header


def upsert_sector(conn, code, name):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sectors (code, name) VALUES (%s, %s)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """, (code, name))
        return cur.fetchone()[0]


def upsert_industry_group(conn, code, name, id_sector):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO industry_groups (code, name, id_sector) VALUES (%s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """, (code, name, id_sector))
        return cur.fetchone()[0]


def upsert_industry(conn, code, name, id_industry_group):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO industries (code, name, id_industry_group) VALUES (%s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """, (code, name, id_industry_group))
        return cur.fetchone()[0]


def upsert_sub_industry(conn, code, name, description, id_industry):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sub_industries (code, name, description, id_industry) VALUES (%s, %s, %s, %s)
            ON CONFLICT (code) DO
              UPDATE SET name = EXCLUDED.name,
                         description = EXCLUDED.description;
        """, (code, name, description, id_industry))


def main(args):
    DB_PARAMS = {
        'dbname': args.db,
        'user': args.username,
        'password': args.password,
        'host': args.host,
        'port': args.port
    }

    with open(args.csv_path, 'r') as file, psycopg2.connect(**DB_PARAMS) as conn:
        reader = csv.DictReader(file)
        if not verify_csv_header(reader):
            print("{}: header does not match expected structure".format(
                args.csv_path), file=sys.stderr)
            exit(1)

        for row in reader:
            sector_id = upsert_sector(
                conn, int(float(row['sector_code'])), row['sector_name'])
            industry_group_id = upsert_industry_group(conn, int(
                float(row['industry_group_code'])), row['industry_group_name'], sector_id)
            industry_id = upsert_industry(conn, int(
                float(row['industry_code'])), row['industry_name'], industry_group_id)
            upsert_sub_industry(
                conn, int(row['sub_industry_code']), row['sub_industry_name'],
                row['industry_description'], industry_id)
        conn.commit()


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)
