# GICS Transfomer

This Python script processes an XLSX file containing the official Global Industry Classification
Standard (GICS) released by MSCI. It transforms and normalizes the data, outputting the results as a
CSV file.

## Features

- Reads GICS data from an Excel (XLSX) file.
- Normalizes column names and data structure.
- Handles merged cells and multi-row entries.
- Option to remove discontinued classifications.
- Outputs processed data to a CSV file.

## Requirements

- Python 3.x
- pandas
- numpy
- openpyxl

## Installation

To get started with the GICS Transformer project, clone the repository and install the required
dependencies:

```bash
git clone https://github.com/midsbie/gics-transformer.git
cd gics-transformer
pip install -r requirements.txt
```

## Usage

To run the GICS Transformer script and convert GICS data to CSV format, use the following command:

```bash
python src/gics2csv.py input_file [--output=output.csv] [--drop-discontinued=true/false]
```

Replace `input_file` with the path to your input data file. The `--output` argument is optional and
specifies the path to the output CSV file. The `--drop-discontinued` argument is also optional and
indicates whether to remove discontinued classifications (default is `false`).

### GICS Data Source

The GICS data sheet can be found at the following link: [MSCI GICS Structure and
Definitions](https://www.msci.com/documents/1296102/29559863/GICS_structure_and_definitions_effective_close_of_March_17_2023.xlsx/e47b8086-56fd-c9d2-196f-c2054b24b1d4?t=1670964718735)

You can download this sheet and use it as the input file for the GICS Transformer script.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and
create. All contributions are greatly appreciated.

## License

Distributed under the MIT License. See LICENSE for more information.
