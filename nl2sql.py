#!/usr/bin/python3
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import wordnet
from nltk import word_tokenize
from nltk import pos_tag

from .database import Database
from .keywordCorpus import KeywordCorpus
from .thesaurus import Thesaurus
from .constants import Color, without_color
from .parser import Parser

class Nl2Sql:
    def __init__(self, database_path, lang_config_path
    , thesaurus_path = None, color = False):
    
        if color == False:
            without_color()
        
        database = Database()

        if thesaurus_path:
            thesaurus = Thesaurus()
            thesaurus.load(thesaurus_path)
            database.set_thesaurus(thesaurus)
        
        database.load(database_path)

        config = KeywordCorpus()
        config.load(lang_config_path)

        # database.print_me()

        self.parser = Parser(database, config)
        # self.json_output_path = json_output_path

    def get_sql_query(self, nl_sentence):

        tokens = word_tokenize(nl_sentence.lower())

        # stop_words = set(stopwords.words('english'))
        # tokens = [i for i in tokens if not i in stop_words]

        tagged = pos_tag(tokens)

        wnl = WordNetLemmatizer()
        # print(tagged)
        
        tokens = []

        for i in tagged:
            tag = self.get_wordnet_tag(i[1])
            if tag is None:
                tokens.append(wnl.lemmatize(i[0]))
            else:
                tokens.append(wnl.lemmatize(i[0],tag))

        input_sentence = ' '.join(tokens)
        # print(input_sentence)
        queries = self.parser.parse_sentence(input_sentence)

        full_query = ''

        for query in queries:
            full_query += str(query)
            print(query)

        return full_query

    def get_wordnet_tag(self,tag):
        if tag.startswith('J'):
            return 'v'
        if tag.startswith('V'):
            return 'v'
        elif tag.startswith('N'):
            return 'n'
        elif tag.startswith('R'):
            return 'r'
        else:
            return None