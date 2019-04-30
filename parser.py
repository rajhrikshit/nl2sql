import sys
import string
import re
from threading import Thread
import functools
import unicodedata

from .parseException import ParseException
from .query import Select, From, Join, Where, Query, Condition, GroupBy, OrderBy

class SelectParser(Thread):
    def __init__(self, columns_of_select, tables_of_from, select_phrase, count_keywords, sum_keywords, average_keywords,
                 max_keywords, min_keywords, distinct_keywords, dict_database, obj_database):
        Thread.__init__(self)
        self.select_objects = []
        self.columns_of_select = columns_of_select
        self.tables_of_from = tables_of_from
        self.select_phrase = select_phrase
        self.count_keywords = count_keywords
        self.sum_keywords = sum_keywords
        self.average_keywords = average_keywords
        self.max_keywords = max_keywords
        self.min_keywords = min_keywords
        self.distinct_keywords = distinct_keywords
        self.dict_database = dict_database
        self.obj_database = obj_database
        
    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.dict_database:
            if column in self.dict_database[table]:
                tmp_table.append(table)
        return tmp_table
    
    def get_column_name_with_alias_table(self, column, table_of_from):
        tables_of_column = self.get_tables_of_column(column)
        first_table_of_column = tables_of_column[0]
        
        if table_of_from in tables_of_column:
            return str(table_of_from)+'.'+str(column)
        else:
            return str(first_table_of_column)+'.'+str(column)
        
    def uniquify(self, list):
        un_list = []
        for e in list:
            if e not in un_list:
                un_list.append(e)
        
        return un_list
    
    def run(self):

        # print("Phrase ",self.select_phrase)
        for table_of_from in self.tables_of_from:
            self.select_object = Select()
            #is_count = False
            self.columns_of_select = self.uniquify(self.columns_of_select)
            number_of_select_columns = len(self.columns_of_select)
            
            if number_of_select_columns == 0:
                select_type = []
                # lower_select_phrase = ' '.join(word.lower() for word in self.select_phrase)
                
                for count_keyword in self.count_keywords:
                    lower_select_phrase = ' '.join(word.lower() for word in self.select_phrase)
                    if count_keyword in lower_select_phrase:
                        select_type.append('COUNT')
                        break
                
                for distinct_keyword in self.distinct_keywords:
                    lower_select_phrase = ' '.join(word.lower() for word in self.select_phrase)
                    if distinct_keyword in lower_select_phrase:
                        select_type.append('DISTINCT')
                        break
                self.select_object.add_column(None,self.uniquify(select_type))
            else:
                select_phrases = []
                previous_index = 0
                
                for i in range(0, len(self.select_phrase)):
                    for column_name in self.columns_of_select:
                        # print(self.select_phrase[i],"-----",column_name)
                        # print(self.obj_database.get_column_with_this_name(column_name).equivalences)
                        if (self.select_phrase[i] == column_name) or (
                                self.select_phrase[i] in self.obj_database.get_column_with_this_name(column_name).equivalences):
                            # print("Appending")
                            select_phrases.append(self.select_phrase[previous_index : i+1])
                            previous_index = i+1
                select_phrases.append(self.select_phrase[previous_index : ])
                
                for i in range(0, len(select_phrases)):
                    select_type = []
                    
                    lower_phrase = [word.lower() for word in select_phrases[i]]
                    # print(lower_phrase)
                    
                    for keyword in self.average_keywords:
                        if keyword in lower_phrase:
                            select_type.append('AVG')
                            
                    for keyword in self.count_keywords:
                        if keyword in lower_phrase:
                            select_type.append('COUNT')
                    
                    for keyword in self.max_keywords:
                        if keyword in lower_phrase:
                            select_type.append('MAX')
                            
                    for keyword in self.min_keywords:
                        if keyword in lower_phrase:
                            select_type.append('MIN')
                    
                    for keyword in self.sum_keywords:
                        if keyword in lower_phrase:
                            select_type.append('SUM')
                    
                    for keyword in self.distinct_keywords:
                        if keyword in lower_phrase:
                            select_type.append('DISTINCT')
                    
                    # print(self.columns_of_select[i]," ",select_type)

                    if (i != len(select_phrases) - 1):# or (select_type is not None     
                        column = self.get_column_name_with_alias_table(self.columns_of_select[i], table_of_from)
                        self.select_object.add_column(column, self.uniquify(select_type))
            # print(self.select_object)
            self.select_objects.append(self.select_object)
            
    def join(self):
        Thread.join(self)
        return self.select_objects
       

class FromParser(Thread):
    def __init__(self, tables_of_from, columns_of_select, columns_of_where, obj_database):
        Thread.__init__(self)
        self.queries = []
        self.tables_of_from = tables_of_from
        self.columns_of_select = columns_of_select
        self.columns_of_where = columns_of_where

        self.obj_database = obj_database
        self.dict_database = self.obj_database.get_tables_into_dictionary()
        
    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.dict_database:
            if column in self.dict_database[table]:
                tmp_table.append(table)
        return tmp_table
    
    def intersects(self, a, b):
        return list(set(a) & set(b))
    
    def difference(self, a, b):
        diff = []
        for e in a:
            if e not in b:
                diff.append(e)
        return diff
    
    def is_direct_join_possible(self, table_src, table_trg):
        fk_column_of_src_table = self.obj_database.get_foreign_keys_of_table(table_src)
        fk_column_of_trg_table = self.obj_database.get_foreign_keys_of_table(table_trg)
        
        for fk in fk_column_of_src_table:
            if fk.is_foreign()['foreign_table'] == table_trg:
                return [(table_src, fk.name), (table_trg, fk.is_foreign()['foreign_column'])]
        
        for fk in fk_column_of_trg_table:
            if fk.is_foreign()['foreign_table'] == table_src:
                return [(table_src, fk.is_foreign()['foreign_column']),(table_trg, fk.name)]
        
        return None
    
    def get_all_direct_linked_tables_of_a_table(self, src_table):
        links = []
        
        for trg_table in self.dict_database:
            link = self.is_direct_join_possible(src_table, trg_table)
            if link is not None:
                links.append(link)
        return links
    
    def is_join(self, historic, table_src, table_trg):
        historic = historic
        links = self.get_all_direct_linked_tables_of_a_table(table_src)
        
        differences = []
        
        for join in links:
            if join[1][0] not in historic:
                differences.append(join)
        links = differences
        
        for join in links:
            if join[1][0] == table_trg:
                return [0,join]
        
        path = []
        historic.append(table_src)
        
        for join in links:
            result = [1, self.is_join(historic, join[1][0], table_trg)]
            if result[1] != []:
                if result[0] == 0:
                    path.append(result[1])
                    path.append(join)
                else:
                    path = result[1]
                    path.append(join)
        
        return path
    
    def get_link(self, table_src, table_trg):
        path = self.is_join([], table_src, table_trg)
        
        if len(path) > 0:
            path.pop(0)
            path.reverse()
        return path
    
    def unique(self, _list):
        return  [list(x) for x in set(tuple(x) for x in _list)]
    
    def unique_order(self, _list):
        un_list = []
        for element in _list:
            if element not in un_list:
                un_list.append(element)
        
        return un_list
    
    def run(self):
        self.queries = []
        
        for table_of_from in self.tables_of_from:
            links = []
            query = Query()
            query.set_from(From(table_of_from))
            join_object = Join()
            
            for column in self.columns_of_select:
                if column not in self.dict_database[table_of_from]:
                    foreign_table = self.get_tables_of_column(column)[0]
                    join_object.add_table(foreign_table)
                    link = self.get_link(table_of_from, foreign_table)
                    
                    if not link:
                        self.queries = ParseException("There is at least column "
                                                      + column + " that is unreachable from table " + table_of_from.upper() + " !")
                        return
                    else:
                        links.extend(link)
            
            for column in self.columns_of_where:
                if column not in self.dict_database[table_of_from]:
                    foreign_table = self.get_tables_of_column(column)[0]
                    join_object.add_table(foreign_table)
                    link = self.get_link(table_of_from, foreign_table)
                    
                    if not link:
                        self.queries = ParseException("There is at least column "
                                                      + column + " that is unreachable from table " + table_of_from.upper() + " !")
                        return
                    else:
                        links.extend(link)
            
            join_object.set_links(self.unique_order(links))
            query.set_join(join_object)
            self.queries.append(query)
            
    
    def join(self):
        Thread.join(self)
        return self.queries
    

class WhereParser(Thread):
    def __init__(self, where_phrases, tables_of_from, columns_of_values_of_where, count_keywords, sum_keywords,
                 average_keywords, max_keywords, min_keywords, greater_keywords, less_keywords, between_keywords,
                 negation_keywords, junction_keywords, disjunction_keywords, like_keywords, distinct_keywords,
                 dict_database, obj_database):
        Thread.__init__(self)
        self.where_objects = []
        self.where_phrases = where_phrases
        self.tables_of_from = tables_of_from
        self.columns_of_values_of_where = columns_of_values_of_where
        self.count_keywords = count_keywords
        self.sum_keywords = sum_keywords
        self.average_keywords = average_keywords
        self.max_keywords = max_keywords
        self.min_keywords = min_keywords
        self.greater_keywords = greater_keywords
        self.less_keywords = less_keywords
        self.between_keywords = between_keywords
        self.negation_keywords = negation_keywords
        self.junction_keywords = junction_keywords
        self.disjunction_keywords = disjunction_keywords
        self.like_keywords = like_keywords
        self.distinct_keywords = distinct_keywords
        self.dict_database = dict_database
        self.obj_database = obj_database
    
    
        
    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.dict_database:
            if column in self.dict_database[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        tables_of_column = self.get_tables_of_column(column)
        first_table_of_column = tables_of_column[0]
        
        if table_of_from in tables_of_column:
            return str(table_of_from)+'.'+str(column)
        else:
            return str(first_table_of_column)+'.'+str(column)

    def intersect(self, a, b):
        return list(set(a) & set(b))
    
    def predict_operation_type(self, previous_column_offset, current_column_offset):
        interval_offset = list(range(previous_column_offset, current_column_offset))
        if (len(self.intersect(interval_offset, self.count_keyword_offset)) >= 1):
            return 'COUNT'
        elif (len(self.intersect(interval_offset, self.sum_keyword_offset)) >= 1):
            return 'SUM'
        elif (len(self.intersect(interval_offset, self.average_keyword_offset)) >= 1):
            return 'AVG'
        elif (len(self.intersect(interval_offset, self.max_keyword_offset)) >= 1):
            return 'MAX'
        elif (len(self.intersect(interval_offset, self.min_keyword_offset)) >= 1):
            return 'MIN'
        else:
            return None
    
    def predict_operator(self, current_column_offset, next_column_offset):
        interval_offset = list(range(current_column_offset, next_column_offset))

        if (len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1) and (
                    len(self.intersect(interval_offset, self.greater_keyword_offset)) >= 1):
            return '<'
        elif (len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1) and (
                    len(self.intersect(interval_offset, self.less_keyword_offset)) >= 1):
            return '>'
        if (len(self.intersect(interval_offset, self.less_keyword_offset)) >= 1):
            return '<'
        elif (len(self.intersect(interval_offset, self.greater_keyword_offset)) >= 1):
            return '>'
        elif (len(self.intersect(interval_offset, self.between_keyword_offset)) >= 1):
            return 'BETWEEN'
        elif (len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1):
            return '!='
        elif (len(self.intersect(interval_offset, self.like_keyword_offset)) >= 1):
            return 'LIKE'
        else:
            return '='
        
    def predict_junction(self, previous_column_offset, current_column_offset):
        interval_offset = list(range(previous_column_offset, current_column_offset))
        #junction = 'AND'
        if (len(self.intersect(interval_offset, self.disjunction_keyword_offset)) >= 1):
            return 'OR'
        elif (len(self.intersect(interval_offset, self.junction_keyword_offset)) >= 1):
            return 'AND'

        first_encountered_junction_offset = -1
        first_encountered_disjunction_offset = -1

        for offset in self.junction_keyword_offset:
            if offset >= current_column_offset:
                first_encountered_junction_offset = offset
                break

        for offset in self.disjunction_keyword_offset:
            if offset >= current_column_offset:
                first_encountered_disjunction_offset = offset
                break

        if first_encountered_junction_offset >= first_encountered_disjunction_offset:
            return 'AND'
        else:
            return 'OR'
    
    def uniquify(self, _list):
        un_list = []
        for e in _list:
            if e not in un_list:
                un_list.append(e)
        
        return un_list
    
    def run(self):
        number_of_where_columns = 0
        columns_of_where = []
        offset_of = {}
        column_offset = []
        self.count_keyword_offset = []
        self.sum_keyword_offset = []
        self.average_keyword_offset = []
        self.max_keyword_offset = []
        self.min_keyword_offset = []
        self.greater_keyword_offset = []
        self.less_keyword_offset = []
        self.between_keyword_offset = []
        self.junction_keyword_offset = []
        self.disjunction_keyword_offset = []
        self.negation_keyword_offset = []
        self.like_keyword_offset = []
        
        # print("Where Parser: ",self.where_phrases)

        for phrase in self.where_phrases:
            phrase_offset_string = ''
            for i in range(0, len(phrase)):
                for table_name in self.dict_database:
                    columns = self.obj_database.get_table_by_name(table_name).get_columns()
                    for column in columns:
                        if (phrase[i] == column.name) or (phrase[i] in column.equivalences):
                            number_of_where_columns += 1
                            columns_of_where.append(column.name)
                            offset_of[phrase[i]] = i
                            column_offset.append(i)
                            break
                    else:
                        continue
                    break
                        
                
                phrase_keyword = str(phrase[i]).lower() #Current word in the phrase
                phrase_offset_string += phrase_keyword + " "
                
                for keyword in self.count_keywords:
                    if keyword in phrase_offset_string:
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string)): # To find if the keyword is just appended
                            self.count_keyword_offset.append(i)
                
                for keyword in self.sum_keywords:
                    if keyword in phrase_offset_string :    # before the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.sum_keyword_offset.append(i)

                for keyword in self.average_keywords:
                    if keyword in phrase_offset_string :    # before the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.average_keyword_offset.append(i)

                for keyword in self.max_keywords:
                    if keyword in phrase_offset_string :    # before the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.max_keyword_offset.append(i)

                for keyword in self.min_keywords:
                    if keyword in phrase_offset_string :    # before the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.min_keyword_offset.append(i)

                for keyword in self.greater_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.greater_keyword_offset.append(i)

                for keyword in self.less_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.less_keyword_offset.append(i)

                for keyword in self.between_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.between_keyword_offset.append(i)

                for keyword in self.junction_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.junction_keyword_offset.append(i)

                for keyword in self.disjunction_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.disjunction_keyword_offset.append(i)

                for keyword in self.negation_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.negation_keyword_offset.append(i)

                for keyword in self.like_keywords:
                    if keyword in phrase_offset_string :    # after the column
                        if (phrase_offset_string.find(keyword) + len(keyword) + 1 == len(phrase_offset_string) ) :
                            self.like_keyword_offset.append(i)
                
        for table_of_from in self.tables_of_from:
            where_object = Where()
            for i in range(0, len(column_offset)):
                current = column_offset[i]

                if i == 0:
                    previous = 0
                else:
                    previous = column_offset[i - 1]

                if i == (len(column_offset) - 1):
                    _next = 999
                else:
                    _next = column_offset[i + 1]

                junction = self.predict_junction(previous, current)
                column = self.get_column_name_with_alias_table(columns_of_where[i], table_of_from)
                operation_type = self.predict_operation_type(previous, current)

                if len(self.columns_of_values_of_where) > i:
                    value = self.columns_of_values_of_where[
                        len(self.columns_of_values_of_where) - len(columns_of_where) + i]
                else:
                    #print("Ooops")
                    value = 'OOV'  # Out Of Vocabulary: default value

                operator = self.predict_operator(current, _next)
                where_object.add_condition(junction, Condition(column, operation_type, operator, value))
            self.where_objects.append(where_object)
            
    
    def join(self):
        Thread.join(self)
        return self.where_objects
            

                    
class GroupByParser(Thread):
    def __init__(self, group_by_phrases, tables_of_from, dict_database, obj_database):
        Thread.__init__(self)
        self.group_by_objects = []
        self.group_by_phrases = group_by_phrases
        self.tables_of_from = tables_of_from
        self.dict_database = dict_database
        self.obj_database = obj_database
        
        
    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.dict_database:
            if column in self.dict_database[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        tables_of_column = self.get_tables_of_column(column)
        first_table_of_column = tables_of_column[0]
        
        if table_of_from in tables_of_column:
            return str(table_of_from)+'.'+str(column)
        else:
            return str(first_table_of_column)+'.'+str(column)    
        
    def run(self):
        for table_of_from in self.tables_of_from:
            group_by_object = GroupBy()
            for phrase in self.group_by_phrases:
                for i in range(0,len(phrase)):
                    for table_name in self.dict_database:
                        columns = self.obj_database.get_table_by_name(table_name).get_columns()
                        for column in columns:
                            if (phrase[i]==column.name) or (phrase[i] in column.equivalences):
                                column_with_alias = self.get_column_name_with_alias_table(column.name , table_of_from)
                                group_by_object.set_column(column_with_alias)
        self.group_by_objects.append(group_by_object)

    def join(self):
        Thread.join(self)
        return self.group_by_objects


class OrderByParser(Thread):
    def __init__(self, order_by_phrases, tables_of_from, asc_keywords, desc_keywords, dict_database, obj_database):
        Thread.__init__(self)
        self.order_by_objects = []
        self.order_by_phrases = order_by_phrases
        self.tables_of_from = tables_of_from
        self.asc_keywords = asc_keywords
        self.desc_keywords = desc_keywords
        self.dict_database = dict_database
        self.obj_database = obj_database
  
    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.dict_database:
            if column in self.dict_database[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        tables_of_column = self.get_tables_of_column(column)
        first_table_of_column = tables_of_column[0]
        
        if table_of_from in tables_of_column:
            return str(table_of_from)+'.'+str(column)
        else:
            return str(first_table_of_column)+'.'+str(column) 
        
    def intersect(self, a, b):
        return list(set(a) & set(b))
    
    def predict_order(self , phrase):
        if(len(self.intersect(phrase, self.desc_keywords))>=1):
            return 'DESC'
        else:
            return 'ASC'

    def run(self):
        for table_of_from in self.tables_of_from:
            order_by_object = OrderBy()
            for phrase in self.order_by_phrases:
                for i in range(0,len(phrase)):
                    for table_name in self.dict_database:
                        columns = self.obj_database.get_table_by_name(table_name).get_columns()
                        for column in columns:
                            if (phrase[i]==column.name) or (phrase[i] in column.equivalences):
                                column_with_alias = self.get_column_name_with_alias_table(column.name , table_of_from)
                                order_by_object.add_column(column_with_alias,self.predict_order(phrase))
        self.order_by_objects.append(order_by_object)

    def join(self):
        Thread.join(self)
        return self.order_by_objects
                                    
class Parser:
    obj_database = None
    dict_database = None

    count_keywords = []
    sum_keywords = []
    average_keywords = []
    max_keywords = []
    min_keywords = []
    junction_keywords = []
    disjunction_keywords = []
    greater_keywords = []
    less_keywords = []
    between_keywords = []
    order_by_keywords = []
    asc_keywords = []
    desc_keywords = []
    group_by_keywords = []
    negation_keywords = []
    equal_keywords = []
    like_keywords = []

    def __init__(self, database, config):
        self.obj_database = database
        self.dict_database = self.obj_database.get_tables_into_dictionary()

        self.count_keywords       = config.get_count_keywords()
        self.sum_keywords         = config.get_sum_keywords()
        self.average_keywords     = config.get_avg_keywords()
        self.max_keywords         = config.get_max_keywords()
        self.min_keywords         = config.get_min_keywords()
        self.junction_keywords    = config.get_junction_keywords()
        self.disjunction_keywords = config.get_disjunction_keywords()
        self.greater_keywords     = config.get_greater_keywords()
        self.less_keywords        = config.get_less_keywords()
        self.between_keywords     = config.get_between_keywords()
        self.order_by_keywords    = config.get_order_by_keywords()
        self.asc_keywords         = config.get_asc_keywords()
        self.desc_keywords        = config.get_desc_keywords()
        self.group_by_keywords    = config.get_group_by_keywords()
        self.negation_keywords    = config.get_negation_keywords()
        self.equal_keywords       = config.get_equal_keywords()
        self.like_keywords        = config.get_like_keywords()
        self.distinct_keywords    = config.get_distinct_keywords()


    @staticmethod
    def _myCmp(s1,s2):
        if len(s1.split()) == len(s2.split()) :
            if len(s1) >= len(s2) :
                return 1
            else:
                return -1
        else:
            if len(s1.split()) >= len(s2.split()):
                return 1
            else:
                return -1


    @classmethod
    def transformation_sort(cls,transition_list):
        # Sort on basis of two keys split length and then token lengths in the respective priority.
        return sorted(transition_list, key=functools.cmp_to_key(cls._myCmp),reverse=True)

    def parse_sentence(self, input_sentence):
        sys.tracebacklimit = 0

        number_of_table = 0
        number_of_select_column = 0
        number_of_where_column = 0
        last_table_position = 0
        columns_of_select = []
        columns_of_where = []
        columns_of_values_of_where = []

        input_sentence = input_sentence.rstrip(string.punctuation.replace('"','').replace("'",''))

        filters = [",","!"]

        for fill in filters :
            input_sentence = input_sentence.replace(fill," ")
        
        input_word_list = input_sentence.split()

        number_of_where_column_temp = 0
        number_of_table_temp = 0
        last_table_position_temp = 0
        

        start_phrase = ''
        mid_phrase = ''
        end_phrase = ''

        

        for i in range(0, len(input_word_list)):
            word = input_word_list[i]
            for table_name in self.dict_database:
                if (word == table_name) or (
                            word in self.obj_database.get_table_by_name(table_name).equivalences):
                    if number_of_table_temp == 0:
                        start_phrase = input_word_list[:i]

                    number_of_table_temp += 1
                    last_table_position_temp = i

                columns = self.obj_database.get_table_by_name(table_name).get_columns()
                for column in columns:
                    if (word == column.name) or (word in column.equivalences):
                        if number_of_where_column_temp == 0:
                            mid_phrase = input_word_list[len(start_phrase):last_table_position_temp + 1]
                        number_of_where_column_temp += 1
                        break
                    else:
                        if (number_of_table_temp != 0) and (number_of_where_column_temp == 0) and (
                                    i == (len(input_word_list) - 1)):
                            mid_phrase = input_word_list[len(start_phrase):]
                

        end_phrase = input_word_list[len(start_phrase) + len(mid_phrase):]

        irext = ' '.join(end_phrase)

        if irext:

            assignment_list =  self.equal_keywords + self.like_keywords + self.greater_keywords + self.less_keywords + self.negation_keywords

            # custom operators added as they can be possibilities
            assignment_list.append(':')
            assignment_list.append('=')

            # Algorithmic logic for best substitution for extraction of values with the help of assigners.
            assignment_list = self.transformation_sort(assignment_list)

            general_assigner = "*res*@3#>>*"
            like_assigner = "*like*@3#>>*"

            for idx, assigner in enumerate(assignment_list):
                if assigner in self.like_keywords:
                    assigner = str(" "+assigner+" ")
                    irext = irext.replace(assigner,str(" "+like_assigner+" "))
                else:
                    assigner = str(" "+assigner+" ")
                    irext = irext.replace(assigner,str(" "+general_assigner+" "))
            
            for i in re.findall("(['\"].*?['\"])",irext):
                irext = irext.replace(i,i.replace(' ','<_>').replace('"','').replace("'",''))
            
            irext_list = irext.split()

            for idx, word in enumerate(irext_list):
                index = idx + 1
                if word == like_assigner and index < len(irext_list) and irext_list[index] != like_assigner and irext_list[index] != general_assigner:
                    columns_of_values_of_where.append(str("'%"+str(irext_list[index]).replace('<_>',' ') + "%'"))
                
                if word == general_assigner and index < len(irext_list) and irext_list[index] != like_assigner and irext_list[index] != general_assigner:
                    columns_of_values_of_where.append(str("'"+str(irext_list[index]).replace('<_>',' ') + "'"))


        
        '''--------------------------------------------------------------------------------------------------------------------------------------------------------'''

        tables_of_from = []
        select_phrase = ''
        from_phrase = ''
        where_phrase = ''

        words = re.findall(r"[\w]+",input_sentence)
        
        for i in range (0,len(words)):

            word = words[i]
            for table_name in self.dict_database:
                if word == table_name or word in self.obj_database.get_table_by_name(table_name).equivalences:
                    if number_of_table == 0:
                        select_phrase = words[:i]
                    tables_of_from.append(table_name)
                    number_of_table += 1
                    last_table_position = i
                
                column_list = self.obj_database.get_table_by_name(table_name).get_columns()
                for column in column_list:
                    if word == column.name or word in column.equivalences:
                        # print(column.equivalences)
                        if number_of_table == 0:
                            columns_of_select.append(column.name)
                            number_of_select_column += 1
                        else:
                            if number_of_where_column == 0:
                                from_phrase = words[len(select_phrase):last_table_position+1]
                            columns_of_where.append(column.name)
                            number_of_where_column += 1
                        break
                    
            
            ### Change --> If condition pulled out from the Loops
            if number_of_table != 0 and number_of_where_column == 0 and i == len(words) - 1:
                from_phrase = words[len(select_phrase) : ]
        
        where_phrase = words[len(select_phrase) + len(from_phrase) : ]

        if(number_of_select_column + number_of_table + number_of_where_column) == 0:
            raise ParseException("No Database Keyword found in your Natural Language query !")
        
        if len(tables_of_from) > 0:
            from_phrases = []
            previous_index = 0
            
            for i in range(0, len(from_phrase)):
                for table in tables_of_from:
                    if(from_phrase[i] == table) or (from_phrase[i] in self.obj_database.get_table_by_name(table).equivalences):
                        from_phrases.append(from_phrase[previous_index : i + 1])
                        previous_index = i+1
            
            last_junction_word_index = -1

            for i in range(0,len(from_phrases)):
                number_of_junction_words = 0
                number_of_disjunction_words = 0

                phrase = from_phrases[i]
                for word in phrase:
                    if word in self.junction_keywords:
                        number_of_junction_words += 1
                    if word in self.disjunction_keywords:
                        number_of_disjunction_words += 1

                if(number_of_junction_words + number_of_disjunction_words) > 0:
                    last_junction_word_index = i
            
            if last_junction_word_index == -1:
                from_phrase = sum(from_phrases[:1],[])
                where_phrase = sum(from_phrases[1:],[]) + where_phrase
            else:
                from_phrase = sum(from_phrases[ : last_junction_word_index + 1], [])
                where_phrase = sum(from_phrases[last_junction_word_index + 1 : ], []) + where_phrase
        
        real_tables_of_from = []

        for word in from_phrase:
            for table in tables_of_from:
                if (word == table) or (word in self.obj_database.get_table_by_name(table).equivalences):
                    real_tables_of_from.append(table)
        
        tables_of_from = real_tables_of_from

        if(len(tables_of_from) == 0):
            raise ParseException("No Table Name found in your Natural Language query !")
        
        group_by_phrase = []
        order_by_phrase = []
        new_where_phrase = []
        previous_index = 0
        previous_phrase_type = 0
        still_where = True

        for i in range(0, len(where_phrase)):
            if where_phrase[i] in self.order_by_keywords:
                if not still_where:
                    if previous_phrase_type == 1:
                        order_by_phrase.append(where_phrase[previous_index : i])
                    elif previous_phrase_type == 2:
                        group_by_phrase.append(where_phrase[previous_index : i])
                else:
                    new_where_phrase.append(where_phrase[previous_index : i])
                
                previous_index = i
                previous_phrase_type = 1
                still_where = False
                
            
            if where_phrase[i] in self.group_by_keywords:
                if not still_where:
                    if previous_phrase_type == 1:
                        order_by_phrase.append(where_phrase[previous_index : i])
                    elif previous_phrase_type == 2:
                        group_by_phrase.append(where_phrase[previous_index : i])
                else:
                    new_where_phrase.append(where_phrase[previous_index : i])
                
                previous_index = i
                previous_phrase_type = 2
                still_where = False
                
        
        if previous_phrase_type == 1:
            order_by_phrase.append(where_phrase[previous_index : ])
        elif previous_phrase_type == 2:
            group_by_phrase.append(where_phrase[previous_index : ])
        else:
            new_where_phrase.append(where_phrase)
            
        try:
            select_parser = SelectParser(columns_of_select, tables_of_from, select_phrase, self.count_keywords,
                                         self.sum_keywords, self.average_keywords, self.max_keywords, self.min_keywords,
                                         self.distinct_keywords, self.dict_database, self.obj_database)
            from_parser = FromParser(tables_of_from, columns_of_select, columns_of_where, self.obj_database)
            where_parser = WhereParser(new_where_phrase, tables_of_from, columns_of_values_of_where,
                                       self.count_keywords, self.sum_keywords, self.average_keywords, self.max_keywords,
                                       self.min_keywords, self.greater_keywords, self.less_keywords,
                                       self.between_keywords, self.negation_keywords, self.junction_keywords,
                                       self.disjunction_keywords, self.like_keywords, self.distinct_keywords,
                                       self.dict_database, self.obj_database)
            group_by_parser = GroupByParser(group_by_phrase, tables_of_from, self.dict_database, self.obj_database)
            order_by_parser = OrderByParser(order_by_phrase, tables_of_from, self.asc_keywords, self.desc_keywords,
                                            self.dict_database, self.obj_database)

            select_parser.start()
            from_parser.start()
            where_parser.start()
            group_by_parser.start()
            order_by_parser.start()

            queries = from_parser.join()
        except:
            raise ParseException("Parsing error occured in thread!")

        if isinstance(queries, ParseException):
            raise queries

        try:
            select_objects = select_parser.join()
            where_objects = where_parser.join()
            group_by_objects = group_by_parser.join()
            order_by_objects = order_by_parser.join()
        except:
            raise ParseException("Parsing error occured in thread!")

        for i in range(0, len(queries)):
            query = queries[i]
            query.set_select(select_objects[i])
            query.set_where(where_objects[i])
            query.set_group_by(group_by_objects[i])
            query.set_order_by(order_by_objects[i])

        return queries


