import argparse

from .nl2sql import Nl2Sql


def main():
    arg_parser = argparse.ArgumentParser(description='A Utility to convert Natural Language to SQL query')
    arg_parser.add_argument('-d', '--database', help='Path to SQL dump file', required=True)
    arg_parser.add_argument('-l', '--language', help='Path to language configuration file', required=True)
    arg_parser.add_argument('-i', '--sentence', help='Input sentence to parse', required=True)
    #arg_parser.add_argument('-j', '--json_output', help='path to JSON output file', default=None)
    arg_parser.add_argument('-t', '--thesaurus', help='path to thesaurus file', default=None)
    #arg_parser.add_argument('-s', '--stopwords', help='path to stopwords file', default=None)

    args = arg_parser.parse_args()

    nl2sql = Nl2Sql(
        database_path=args.database,
        lang_config_path=args.language,
        thesaurus_path=args.thesaurus)
    query = nl2sql.get_sql_query(args.sentence)
    #print(query)

if __name__ == '__main__':
    main()
