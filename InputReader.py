import json
import os
import sys
from enum import Enum


class InputKeywords(Enum):
    """
    Enum Class represents the keywords of the `Input File`
    """
    StoredProcedures = 'StoredProcedures'
    Name = 'Name'
    SampleResponse = 'SampleResponse'
    Root = 'Root'
    Tables = 'Tables'
    SchemaName = 'SchemaName'
    ListRoot = 'ListRoot'
    ItemRoot = 'ItemRoot'


class InputReader:
    def __init__(self, in_fileName: str):
        if os.path.exists(in_fileName):
            with open(os.path.abspath(in_fileName)) as file:
                fileContent = json.load(file)
            self.__Tables = fileContent[InputKeywords.Tables.value]
            self.__StoredProcedures = fileContent[InputKeywords.StoredProcedures.value]
        else:
            print(f"Error: {in_fileName} not found!")
            sys.exit(1)

    def getTables(self) -> list:
        return self.__Tables

    def getStoredProcedures(self) -> list:
        return self.__StoredProcedures


if __name__ == '__main__':
    print('Execute MDEFGenerator.py')
