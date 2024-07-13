import argparse
import re

import pandas as pd
from openpyxl import load_workbook


def create_parser():
    parser = argparse.ArgumentParser(description="""Process an XLSX file that
    contains the official Global Industry Classification Standard (GICS)
    released by MSCI, transforming and normalizing the data, and outputting the
    results as a CSV file.""")
    parser.add_argument("filename", type=str,
                        help="The path to the XLSX file to process.")
    parser.add_argument("--sheet", type=str, default=0,
                        help="Sheet in the XLSX to use. Default: first sheet.")
    parser.add_argument("--output", type=str, default="output.csv",
                        help="Output CSV file name. Default: output.csv.")
    parser.add_argument("--drop-discontinued", type=bool, default=False,
                        help="Remove discontinued classifications. Default: False.")
    return parser


def get_codes_to_remove(filename, sheet):
    wb = load_workbook(filename=filename, data_only=True)
    ws = wb[sheet]

    pattern = r'\(.*?\bdiscontinued\b.*?\)'
    codes = []

    # The code for a classification is added to the `code` array if a cell is
    # found to contain the strikethrough formatting or the word "discontinued"
    # is found enclosed within parentheses in a cell.
    for row in ws.iter_rows():
        for cell in row:
            if not cell.font.strikethrough and not re.search(
                    pattern, str(cell.value), re.IGNORECASE):
                continue

            code = row[6].value
            if code is not None:
                codes.append(code)

            break

    wb.close()
    return codes


def normalize_merged_cols(cols, subject, code_col, name_col):
    tgt_col_idx = cols.index(subject)
    cols[tgt_col_idx] = code_col
    cols[tgt_col_idx + 1] = name_col


def main(args):
    # Get a list of codes to remove (done further down below), if applicable.
    codes_to_remove = get_codes_to_remove(
        args.filename, args.sheet) if args.drop_discontinued else []

    df = pd.read_excel(args.filename, sheet_name=args.sheet, header=None)

    # Identify header row
    header_row = df[df.apply(
        lambda x: x.map(lambda y: "Sector" in str(y))).any(axis=1)].index[0]

    # Reset the header
    df.columns = df.loc[header_row]
    df = df.loc[header_row + 1:]
    df.reset_index(drop=True, inplace=True)

    # Give header columns appropriate names, adding a column for the industry
    # description.
    columns_list = df.columns.tolist()
    normalize_merged_cols(columns_list, 'Sector', 'sector_code', 'sector_name')
    normalize_merged_cols(columns_list, 'Industry Group',
                          'industry_group_code', 'industry_group_name')
    normalize_merged_cols(columns_list, 'Industry',
                          'industry_code', 'industry_name')
    normalize_merged_cols(columns_list, 'Sub-Industry',
                          'sub_industry_code', 'sub_industry_name')
    df.columns = columns_list
    df['industry_description'] = ''

    # Copy industry description from the next row
    for i, row in df.iterrows():
        if i < len(df) - 1:
            df.at[i, 'industry_description'] = df.at[i + 1, 'sub_industry_name']

    # Remove every second row containing the descriptions that we've just copied
    df = df.iloc[::2].reset_index(drop=True)

    # Remove rows that refer to classifications that have been discontinued
    if args.drop_discontinued and len(codes_to_remove) > 0:
        df = df[~df['sub_industry_code'].isin(codes_to_remove)]

    # Fix whitespace before filling NA
    df = df.apply(lambda x: x.map(
        lambda y: y.strip() if isinstance(y, str) else y))
    df = df.apply(lambda x: x.map(lambda y: y.replace(
        '\n', '') if isinstance(y, str) else y))
    df['sector_code'] = df['sector_code'].replace('', pd.NA)

    # Make it so all NA columns inherit the content of the preceding row
    df['sector_code'] = df['sector_code'].ffill()
    df['sector_name'] = df['sector_name'].ffill()
    df['industry_group_code'] = df['industry_group_code'].ffill()
    df['industry_group_name'] = df['industry_group_name'].ffill()
    df['industry_code'] = df['industry_code'].ffill()
    df['industry_name'] = df['industry_name'].ffill()
    df['sub_industry_code'] = df['sub_industry_code'].ffill()
    df['sub_industry_name'] = df['sub_industry_name'].ffill()

    # Fixing more oddities:
    # - Collapse multiple spaces into one
    df = df.replace(r'\s\s+', ' ', regex=True)
    # - Remove in-column annotations
    df = df.replace(r'\([^)]*\)', '', regex=True)

    # Done!  Persist to CSV file.
    df.to_csv(args.output, index=False)


if __name__ == '__main__':
    parser = create_parser()
    main(parser.parse_args())
