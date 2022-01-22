"""
Represents the `MDEF Entities`
"""
import re
from InputReader import InputKeywords

replaceValue = '#ReplaceThis'


def isNoneOrEmpty(*args):
    """Checks if any of the given argument is None or Empty."""
    return any(map(lambda inArgs: inArgs is None or len(inArgs) == 0, args))


class MDEFEntity:
    """Represents the `MDEF Entities` (Tables & Stored Procedures)"""

    def __init__(self, in_entityData: dict):
        self.__Name = in_entityData[InputKeywords.Name.name]
        self.__SampleResponse = in_entityData[InputKeywords.SampleResponse.name]

    def __parse(self):
        """Parses the Sample Response"""

    def getName(self):
        return self.__Name

    def getSampleResponse(self):
        return self.__SampleResponse

    @staticmethod
    def findType(in_value):
        """Finds the type of input data"""
        if isinstance(in_value, list):
            return 0
        elif re.match('(\d{4}-\d{2}-\d{2}([TWZ ]*)\d{2}:\d{2}:\d{2})([+-]*)([0-9]*)([:]*)([0-9]*)', str(in_value)) \
                is not None:
            return {
                'SQLType': 'SQL_DATETIME'
            }
        elif isinstance(in_value, bool):
            return {
                'SQLType': 'SQL_BIT'
            }
        elif isinstance(in_value, str):
            return {
                'SQLType': 'SQL_VARCHAR',
                'Length': 512
            }
        elif isinstance(in_value, int):
            return {
                'SQLType': 'SQL_INTEGER',
                'IsUnsigned': False
            } if int(in_value) < (2 ** 32) else {
                'SQLType': 'SQL_BIGINT',
                'IsUnsigned': False
            }
        elif isinstance(in_value, float):
            return {
                'SQLType': 'SQL_DOUBLE',
                'IsUnsigned': False
            }
        elif isinstance(in_value, dict):
            return 1
        else:
            return {
                'SQLType': 'SQL_VARCHAR',
                'Length': 8192
            }

    @staticmethod
    def formatName(in_name: str, is_tableName: bool = False):
        name = ''
        capitalize = True
        nameLen, index = len(in_name), 0
        for ch in in_name:
            if not ch.isalnum():
                capitalize = True
                if not is_tableName and 0 < index < nameLen - 1:
                    name += '_'
            else:
                if capitalize:
                    name += ch.upper()
                    capitalize = not capitalize
                else:
                    name += ch
            index += 1
        return name


class Table(MDEFEntity):
    """Represents the `MDEF Table`"""

    def __init__(self, in_tableData: dict):
        super().__init__(in_tableData)
        self.__SchemaName = in_tableData[InputKeywords.SchemaName.name]
        self.__ListRoot = list() if isNoneOrEmpty(in_tableData[InputKeywords.ListRoot.name]) \
            else str(in_tableData[InputKeywords.ListRoot.name]).split('.')
        self.__ItemRoot = list() if isNoneOrEmpty(in_tableData[InputKeywords.ItemRoot.name]) \
            else str(in_tableData[InputKeywords.ItemRoot.name]).split('.')
        self.__Table = dict()

    def __parse(self):
        """Parses the Sample Response for `Table`"""
        self.__Table['TableName'] = self.getName()
        self.__Table['PKeyColumn'] = {
            f"pk_{self.__Table['TableName']}": [
                {
                    'PKColumnName': replaceValue,
                    'RelatedFKColumns': []
                }
            ]
        }
        self.__Table['FKeyColumn'] = [
            {
                'ForeignKeyColumns': {
                    replaceValue: replaceValue
                },
                'ReferenceTable': replaceValue,
                'ReferenceTableSchema': replaceValue
            }
        ]
        self.__Table['ItemEndpointColumnNames'] = list()
        self.__Table['Sortable'] = False
        self.__Table['Pageable'] = True
        self.__Table['Pagination'] = {
            "SvcReqParam_PageSize": replaceValue,
            "MaxPageSize": 100,
            "SvcReqParam_Offset": replaceValue,
            "OffsetIsByItem": False,
            "PaginationType": replaceValue,
            "SvcRespAttr_TerminationElement": replaceValue
        }
        self.__Table['ColumnPushdown'] = {
            'Support': False,
            'SvcReqParam_Key': [
                replaceValue
            ],
            'SvcReqParam_Value': [','.join(self.getSampleResponse().keys())],
            'SvcReqParam_Delimiter': ','
        }
        columns = list()
        virtualTables = list()
        self.__parseColumns(columns, self.getSampleResponse(), virtualTables, self.__ListRoot, self.__ItemRoot,
                            list(), self.__ListRoot, self.__ItemRoot)
        if len(columns) > 0:
            self.__Table['Columns'] = columns
        else:
            print('Error: No Columns could be generated!')
        if len(virtualTables) > 0:
            self.__Table['VirtualTables'] = virtualTables

        self.__Table['APIAccess'] = {
            'ReadAPI': {
                'Method': 'GET',
                'ColumnRequirements': [],
                'BodySkeleton': '',
                'DataPath': '',
                'Endpoint': {
                    'ListEndpoint': replaceValue,
                    'ItemEndpoint': replaceValue,
                    'Type': 'ENDPOINT_ONLY'
                },
                'Accept': 'application/json',
                'ContentType': 'application/json',
                'ParameterFormat': 'URL',
                'ListRoot': '.'.join(self.__ListRoot),
                'ItemRoot': '.'.join(self.__ItemRoot)
            }
        }
        self.__Table['TableSchemaName'] = self.__SchemaName

    def __parseColumns(self, in_columns: list, in_data: dict, in_virtualTables: list, in_listRootPrefix: list,
                       in_itemRootPrefix: list, in_columnPrefix: list, in_srcListAttr: list = None, in_srcItemAttr: list = None):
        """Parses the response data to generate columns"""
        for colName, colValue in in_data.items():
            sqlType = MDEFEntity.findType(colValue)
            if sqlType == 0:
                in_virtualTables.append(
                    self.__prepareVirtualTable(colValue, list(), list(),
                                               in_columnPrefix + [colName], in_srcListAttr + [colName], in_srcItemAttr + [colName])
                )
            elif sqlType == 1:
                if len(colValue) > 0:
                    self.__parseColumns(in_columns, colValue, in_virtualTables, in_listRootPrefix + [colName],
                                        in_itemRootPrefix + [colName], in_columnPrefix + [colName],
                                        in_srcListAttr + [colName], in_srcItemAttr + [colName])
                else:
                    in_columns.append({
                        'Name': self.formatName('_'.join(in_columnPrefix + [colName]), False),
                        'Metadata': {
                            "SQLType": "SQL_LONGVARCHAR",
                            "Length": 200000000
                        },
                        'Nullable': True,
                        'Updatable': True,
                        'Passdownable': False,
                        'SvcRespAttr_ListResult': '.'.join(in_listRootPrefix + [colName]),
                        'SvcRespAttr_ItemResult': '.'.join(in_itemRootPrefix + [colName]),
                        'SvcReqParam_QueryMapping': '_'.join(in_columnPrefix + [colName])
                    })
            else:
                in_columns.append({
                    'Name': self.formatName('_'.join(in_columnPrefix + [colName]), False),
                    'Metadata': sqlType,
                    'Nullable': True,
                    'Updatable': True,
                    'Passdownable': False,
                    'SvcRespAttr_ListResult': '.'.join(in_listRootPrefix + [colName]),
                    'SvcRespAttr_ItemResult': '.'.join(in_itemRootPrefix + [colName]),
                    'SvcReqParam_QueryMapping': '_'.join(in_columnPrefix + [colName])
                })

    def __prepareVirtualTable(self, in_data: dict, in_listRootPrefix: list, in_itemRootPrefix: list,
                              in_columnPrefix: list, in_srcListAttr: list = None, in_srcItemAttr: list = None) -> dict:
        virtualTable = dict()
        virtualTable['TableName'] = self.formatName('_'.join(in_columnPrefix), is_tableName=True)
        virtualTable['PKeyColumn'] = {
            f"pk_{virtualTable['TableName']}": [
                {
                    'PKColumnName': replaceValue,
                    'RelatedFKColumns': []
                }
            ]
        }
        virtualTable['FKeyColumn'] = [
            {
                'ForeignKeyColumns': {
                    replaceValue: replaceValue
                },
                'ReferenceTable': replaceValue,
                'ReferenceTableSchema': replaceValue
            }
        ]
        virtualTable['SourceAttribute'] = {
            'SvcRespAttr_ListResult': '.'.join(in_srcListAttr),
            'SvcRespAttr_ItemResult': '.'.join(in_srcItemAttr),
            'Pushdown_Mapping': '_'.join(in_columnPrefix)
        }
        columns = list()
        virtualTables = list()
        in_data = in_data[0] if len(in_data) > 0 else {}
        sqlType = self.findType(in_data)
        if sqlType == 1:
            self.__parseColumns(columns, in_data, virtualTables, in_listRootPrefix, in_itemRootPrefix, in_columnPrefix,
                                list(), list())
        if len(columns) > 0:
            virtualTable['Columns'] = columns
        else:
            colName = self.formatName('_'.join(in_columnPrefix), is_tableName=False)
            virtualTable['Columns'] = [
                {
                    'Name': f"{colName}_Index",
                    "Metadata": {
                        "SQLType": "SQL_INTEGER",
                        "IsUnsigned": True
                    },
                    "Nullable": True,
                    "Updatable": False,
                    "Passdownable": False,
                    "SyntheticIndexColumn": True
                },
                {
                    'Name': colName,
                    "Metadata": {
                        "SQLType": "SQL_LONGVARCHAR",
                        "Length": 200000000
                    },
                    "Nullable": True,
                    "Updatable": False,
                    "Passdownable": False,
                    "SvcRespAttr_ListResult": "",
                    "SvcRespAttr_ItemResult": "",
                    "SvcReqParam_QueryMapping": ""
                }
            ]
        if len(virtualTable) > 0:
            virtualTable['VirtualTables'] = virtualTables
        return virtualTable

    def get(self):
        if len(self.__Table) > 0:
            return self.__Table
        else:
            self.__parse()
            return self.__Table


class StoredProcedure(MDEFEntity):
    """Represents the `MDEF Stored Procedure`"""
    def __init__(self, in_storedProcedureData: dict):
        super().__init__(in_storedProcedureData)
        self.__Root = list() if isNoneOrEmpty(in_storedProcedureData[InputKeywords.Root.name]) \
            else str(in_storedProcedureData[InputKeywords.Root.name]).split('.')
        self.__StoredProcedure = dict()

    def __parse(self):
        """Parses the Sample Response for `Stored Procedure`"""
        self.__StoredProcedure['Name'] = self.getName()
        self.__StoredProcedure['ProcedureType'] = 'SIMPLE'
        self.__StoredProcedure['Endpoint'] = replaceValue
        self.__StoredProcedure['Headers'] = {
            'Content-Type': "application/json",
            'Accept': "application/json"
        }
        self.__StoredProcedure['Method'] = 'GET'
        self.__StoredProcedure['ProcedureParameters'] = [
            {
                'Index': 0,
                'Key': replaceValue,
                'ShouldEncode': False,
                'SQLType': replaceValue
            }
        ]
        self.__StoredProcedure['ResultType'] = 'JSONTABLE'
        columns = []
        self.__parseColumns(columns, self.getSampleResponse(), self.__Root, list())
        self.__StoredProcedure['ResultTable'] = {
            'Columns': columns
        }

    def __parseColumns(self, in_columns: list, in_data: dict, in_itemRootPrefix: list, in_columnPrefix: list):
        """Parses the response data to generate columns"""
        for colName, colValue in in_data.items():
            sqlType = MDEFEntity.findType(colValue)
            if sqlType == 1:
                if len(dict(colValue)) > 0:
                    self.__parseColumns(in_columns, colValue, in_itemRootPrefix + [colName],
                                        in_columnPrefix + [colName])
                else:
                    in_columns.append({
                        'Name': self.formatName('_'.join(in_columnPrefix + [colName]), False),
                        'Metadata': {
                            "SQLType": "SQL_LONGVARCHAR",
                            "Length": 200000000
                        },
                        'Nullable': True,
                        'SvcRespAttr_ItemResult': '.'.join(in_itemRootPrefix + [colName])
                    })
            else:
                if sqlType == 0:
                    sqlType = {
                        "SQLType": "SQL_LONGVARCHAR",
                        "Length": 200000000
                    }
                in_columns.append({
                    'Name': self.formatName('_'.join(in_columnPrefix + [colName]), False),
                    'Metadata': sqlType,
                    'Nullable': True,
                    'SvcRespAttr_ItemResult': '.'.join(in_itemRootPrefix + [colName])
                })

    def get(self):
        if len(self.__StoredProcedure) > 0:
            return self.__StoredProcedure
        else:
            self.__parse()
            return self.__StoredProcedure


if __name__ == '__main__':
    print('Execute MDEFGenerator.py')
