from .constants import Color


class Select():
    def __init__(self):
        self.columns = []
    
    def add_column(self, column, column_type):
        if [column, column_type] not in self.columns:
            self.columns.append([column, column_type])
    
    def get_column(self):
        return self.columns
    
    def get_just_column_name(self, column):
        if column != str(None):
            return column.rsplit('.', 1)[1]
        else:
            return column
    
    def  print_column(self, selected_column):
        column = selected_column[0]
        column_type = selected_column[1]
        
        if column is None:
            if column_type is not None:
                if 'COUNT' in column_type:
                    return Color.BOLD + 'COUNT(' + Color.END + '*' + Color.BOLD + ')' + Color.END
                elif 'DISTINCT' in column_type:
                    return Color.BOLD + 'DISTINCT' + Color.END
                else:
                    return '*'
            else:
                return '*'
        else:
            if 'DISTINCT' in column_type:
                if 'COUNT' in column_type:
                    return Color.BOLD + 'COUNT(DISTINCT ' + Color.END + str(column) + Color.BOLD + ')' + Color.END
                else:
                    return Color.BOLD + 'DISTINCT ' + Color.END + str(column)
            if 'COUNT' in column_type:
                return Color.BOLD + 'COUNT(' + Color.END + str(column) + Color.BOLD + ')' + Color.END
            elif 'AVG' in column_type:
                return Color.BOLD + 'AVG(' + Color.END + str(column) + Color.BOLD + ')' + Color.END
            elif 'SUM' in column_type:
                return Color.BOLD + 'SUM(' + Color.END + str(column) + Color.BOLD + ')' + Color.END
            elif 'MAX' in column_type:
                return Color.BOLD + 'MAX(' + Color.END + str(column) + Color.BOLD + ')' + Color.END
            elif 'MIN' in column_type:
                return Color.BOLD + 'MIN(' + Color.END + str(column) + Color.BOLD + ')' + Color.END
            else:
                return str(column)
    
    def __str__(self):
        select_string = ''
        for i in range(0, len(self.columns)):
            if i == (len(self.columns) - 1):
                select_string += str(self.print_column(self.columns[i]))
            else:
                select_string += str(self.print_column(self.columns[i])) + ', '
                
        return Color.BOLD + 'SELECT ' + Color.END + select_string
    
class From():
    table = ''

    def __init__(self, table=None):
        if table is not None:
            self.table = table
        else:
            self.table = ''

    def set_table(self, table):
        self.table = table

    def get_table(self):
        return self.table

    def __str__(self):
        return '\n' + Color.BOLD + 'FROM ' + Color.END + str(self.table)



class Join():
    tables = []
    links = []

    def __init__(self):
        self.tables = []
        self.links = []

    def add_table(self, table):
        if table not in self.tables:
            self.tables.append(table)

    def set_links(self, links):
        self.links = links

    def get_tables(self):
        return self.tables

    def get_links(self):
        return self.links

    def __str__(self):
        if len(self.links) >= 1:
            string = ''
            for i in range(0, len(self.links)):
                string += '\n' + Color.BOLD + 'INNER JOIN ' + Color.END + str(
                    self.links[i][1][0]) + '\n' + Color.BOLD + 'ON ' + Color.END + str(self.links[i][0][0]) + '.' + str(
                    self.links[i][0][1]) + ' = ' + str(self.links[i][1][0]) + '.' + str(self.links[i][1][1])
            return string
        elif len(self.tables) >= 1:
            if len(self.tables) == 1:
                return '\n' + Color.BOLD + 'NATURAL JOIN ' + Color.END + self.tables[0]
            else:
                string = '\n' + Color.BOLD + 'NATURAL JOIN ' + Color.END
                for i in range(0, len(self.tables)):
                    if i == (len(self.tables) - 1):
                        string += str(self.tables[i])
                    else:
                        string += str(self.tables[i]) + ', '
                return string
        else:
            return ''



class Condition():
    column = ''
    column_type = ''
    operator = ''
    value = ''

    def __init__(self, column, column_type, operator, value):
        self.column = column
        self.column_type = column_type
        self.operator = operator
        self.value = value

    def get_column(self):
        return self.column

    def get_column_type(self):
        return self.column_type

    def get_operator(self):
        return self.operator

    def get_value(self):
        return self.value

    def get_in_list(self):
        return [self.column, self.column_type, self.operator, self.value]

    def get_just_column_name(self, column):
        if column != str(None):
            return column.rsplit('.', 1)[1]
        else:
            return column

    def get_column_with_type_operation(self, column, column_type):
        if column_type is None:
            return self.column
        else:
            return Color.BOLD + str(column_type) + '(' + Color.END + self.column + Color.BOLD + ')' + Color.END

    def get_pretty_operator(self, operator):
        if operator == 'BETWEEN':
            return Color.BOLD + 'BETWEEN' + Color.END + ' OOV ' + Color.BOLD + 'AND' + Color.END
        else:
            return Color.BOLD + operator + Color.END

    def __str__(self):
        return str(self.get_column_with_type_operation(self.column, self.column_type)) + ' ' + str(
            self.get_pretty_operator(self.operator)) + ' ' + str(self.value)

    

class Where():
    conditions = []

    def __init__(self, clause=None):
        if clause is not None:
            self.conditions.append([None, clause])
        else:
            self.conditions = []

    def add_condition(self, junction, clause):
        self.conditions.append([junction, clause])

    def get_conditions(self):
        return self.conditions

    def __str__(self):
        string = ''

        if len(self.conditions) >= 1:
            for i in range(0, len(self.conditions)):
                if i == 0:
                    string += '\n' + Color.BOLD + 'WHERE' + Color.END + ' ' + str(self.conditions[i][1])
                else:
                    string += '\n' + Color.BOLD + str(self.conditions[i][0]) + Color.END + ' ' + str(
                        self.conditions[i][1])

            return string
        else:
            return string


class GroupBy():
    column = None

    def __init__(self, column=None):
        if column is not None:
            self.column = column
        else:
            self.column = None

    def set_column(self, column):
        self.column = column

    def get_column(self):
        return self.column

    def get_just_column_name(self, column):
        if column != str(None):
            return column.rsplit('.', 1)[1]
        else:
            return column

    def __str__(self):
        if self.column is not None:
            return '\n' + Color.BOLD + 'GROUP BY ' + Color.END + str(self.column)
        else:
            return ''



class OrderBy():
    columns = []

    def __init__(self):
        self.columns = []

    def add_column(self, column, order):
        if [column, order] not in self.columns:
            self.columns.append([column, order])

    def get_columns(self):
        return self.columns

    def __str__(self):
        if self.columns != []:
            string = Color.BOLD + 'ORDER BY ' + Color.END
            for i in range(0, len(self.columns)):
                if i == (len(self.columns) - 1):
                    string += self.columns[i][0] + ' ' + Color.BOLD + self.columns[i][1] + Color.END
                else:
                    string += self.columns[i][0] + ' ' + Color.BOLD + self.columns[i][1] + Color.END + ', '
            return '\n' + string
        else:
            return ''



class Query():
    select = None
    _from = None
    join = None
    where = None
    group_by = None
    order_by = None

    def __init__(self, select=None, _from=None, join=None, where=None, group_by=None, order_by=None):
        if select is not None:
            self.select = select
        else:
            self.select = None
        if _from is not None:
            self._from = _from
        else:
            self._from = None
        if join is not None:
            self.join = join
        else:
            self.join = None
        if where is not None:
            self.where = where
        else:
            self.where = None
        if group_by is not None:
            self.group_by = group_by
        else:
            self.group_by = None
        if order_by is not None:
            self.order_by = order_by
        else:
            self.order_by = None

    def set_select(self, select):
        self.select = select

    def get_select(self):
        return self.select

    def set_from(self, _from):
        self._from = _from

    def get_from(self):
        return self._from

    def set_join(self, join):
        self.join = join

    def get_join(self):
        return self.join

    def set_where(self, where):
        self.where = where

    def get_where(self):
        return self.where

    def set_group_by(self, group_by):
        self.group_by = group_by

    def get_group_by(self):
        return self.group_by

    def set_order_by(self, order_by):
        self.order_by = order_by

    def get_order_by(self):
        return self.order_by

    def __str__(self):
        return '\n' + str(self.select) + str(self._from) + str(self.join) + str(self.where) + str(self.group_by) + str(
            self.order_by) + ';\n'
