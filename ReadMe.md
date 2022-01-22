# MDEF Tables & StoredProcedures Generator

## Input Parameters:
1. `InputFileName`  - Name of Input File. i.e input_combined.json (Extension must be .json)
    - Find more details about InputFile below
      1. `Name`           - Name to title Table or StoredProcedures
      2. `SampleResponse` - SampleResponse of for the StoredProcedures and Tables
      - StoredProcedures specific parametres
      3. `Root`           - Name of the root object
      - Tables specific parametres
      4. `SchemaName`           - Name of the schema
      5. `ListRoot`       - Name of the root object from the response of the list-endpoint.
      6. `itemRoot`       - Name of the root object from the response of the item-endpoint.

## Usage:
- To execute MDEFGenerator.exe
    ```bash
      MDEFGenerator.exe input_combined.json
    ```
- To execute MDEFGenerator.py with [Python](https://www.python.org/downloads/)
    ```bash
      python MDEFGenerator.py input_combined.json
    ```

