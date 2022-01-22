import os.path
import sys
import json
from MDEFEntity import Table, StoredProcedure
from InputReader import InputReader


def main(input_file: str):
    inputReader = InputReader(input_file)
    storedProcedures = list()
    tables = list()
    for storedProcedure in inputReader.getStoredProcedures():
        storedProcedures.append(StoredProcedure(storedProcedure).get())

    for table in inputReader.getTables():
        tables.append(Table(table).get())

    fileContent = {
        'StoredProcedures': storedProcedures,
        'Tables': tables
    }
    with open('out_driver.mdef', 'w') as file:
        json.dump(fileContent, file)

    os.system(os.path.abspath('out_driver.mdef'))


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == 'h' or sys.argv[1].lower() == 'help':
            print('========== MDEFGenerator ==========\n'
                  'Author: Vipul Rathod\n'
                  'Version: 1.0.0\n'
                  '-----------------------------------\n'
                  'To execute MDEFGenerator\n'
                  ' -> MDEFGenerator.exe {input-file}\n'
                  '===================================')
        else:
            main(sys.argv[1])
    else:
        print('Error: Invalid Command Syntax.\n'
              'The correct syntax: -> MDEFGenerator.exe {input-file}')
