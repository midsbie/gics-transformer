import pandas as pd
import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="""Process an XLSX file that
    contains official Global Industry Classification Standard (GICS) released by
    MSCI, transforming and normalizing the data, and outputting the results as a CSV
    file.""")
    parser.add_argument("filename", type=str,
                        help="The path to the XLSX file to process.")
    parser.add_argument("--sheet", type=str, default=0,
                        help="Sheet in the XLSX to use. Default: first sheet.")
    parser.add_argument("--output", type=str, default="output.csv",
                        help="Output CSV file name. Default: output.csv.")
    return parser


def normalize_merged_cols(cols, subject, code_col, name_col):
    tgt_col_idx = cols.index(subject)
    cols[tgt_col_idx] = code_col
    cols[tgt_col_idx + 1] = name_col


def main(args):
    # Load the data from the specified file and sheet
    df = pd.read_excel(args.filename, sheet_name=args.sheet, header=None)

    # Identify header row
    header_row = df[df.applymap(
        lambda x: "Sector" in str(x)).any(axis=1)].index[0]

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

    # Remove every second row containing the descriptions
    df = df.iloc[::2].reset_index(drop=True)

    # Fix whitespace before filling NA
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.applymap(lambda x: x.replace('\n', '')
                     if isinstance(x, str) else x)
    df['sector_code'].replace('', pd.NA, inplace=True)

    # Make it so all NA columns inherit the content of the preceding row
    df['sector_code'] = df['sector_code'].fillna(method='ffill')
    df['sector_name'] = df['sector_name'].fillna(method='ffill')
    df['industry_group_code'] = df['industry_group_code'].fillna(
        method='ffill')
    df['industry_group_name'] = df['industry_group_name'].fillna(
        method='ffill')
    df['industry_code'] = df['industry_code'].fillna(method='ffill')
    df['industry_name'] = df['industry_name'].fillna(method='ffill')
    df['sub_industry_code'] = df['sub_industry_code'].fillna(method='ffill')
    df['sub_industry_name'] = df['sub_industry_name'].fillna(method='ffill')

    # Fixing more oddities:
    # - Collapse multiple spaces into one
    df.replace(r'\s\s+', ' ', regex=True, inplace=True)
    # - In-column annotations
    df.replace(r'\([^)]*\)', '', regex=True, inplace=True)

    df.to_csv(args.output, index=False)


if __name__ == '__main__':
    parser = create_parser()
    main(parser.parse_args())
