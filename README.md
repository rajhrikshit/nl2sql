# nl2sql

This is an adaptation of the ***ln2sql*** tool by  ***Jérémy Ferrero***. The previous ln2sql tool is modified to work on a broader range of queries with less errors.

* The changes made are
    * Removed the stopwords file and instead used the nltk.corpus stopwords.
    * Added functionality to define Primary Key while defining the column.
    * Added DISTINCT SELECT clause if no SELECT columns specified.
    * Only for english language.
    * Used POS-tagging to tag words and then Lemmatize them accordingly, so that it works for both 'Student' and 'Students'.

Some modifications improve the working of the previous tool, but simultaneously a few features have been reduced. Will definitely try to include and improve them. :facepunch:
