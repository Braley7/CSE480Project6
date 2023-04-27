"""
Name: Chris Braley
Netid: braleych
PID: A60088768
How long did this project take you?

Sources:
https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
"""
import string
import operator
import json
import os.path
import setuptools

_ALL_DATABASES = []

class Database(object): #Only need 1 database for project 1 so far.
    def __init__(self):
        """
        """
        self.tables = []
        self.name = ""

    def add_table(self, tbl):
        self.tables.append(tbl)

    def get_table(self, name):      # Return tables with matching names
        for tbl in self.tables:
            if name == tbl.name:
                return tbl

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

class Table(object):
    def __init__(self, name):
        self.name = name
        self.types = []
        self.rows = []
        self.colnames = []

    def set_types(self, data):
        for elem in data:
            if elem == "INTEGER" or elem == "TEXT" or elem == "REAL": # Store table types, in order with a list
                self.types.append(elem)
            else:
                self.colnames.append(elem)  # Also store column names

    def add_row(self, data, cols=[]):            # Should be called during INSERT

        if cols:

            lst = []
            for elem in self.colnames:
                flag = False
                for i in range(len(cols)):
                    if elem == cols[i]:
                        lst.append(data[i])
                        flag = True
                if not flag:
                    lst.append(None)

        else:
            lst = []
            for i in range(len(data)):          #Conversions of data eg ('James', 29, 3.5)
                if data[i] is None:
                    lst.append(None)
                    continue
                if data[i] == '?':
                    lst.append(data[i])
                    continue
                if self.types[i] == "INTEGER":
                    lst.append(int(data[i]))
                if self.types[i] == "TEXT":
                    lst.append(str(data[i]))
                if self.types[i] == "REAL":
                    lst.append(float(data[i]))

        row = Row(lst)
        self.rows.append(row)

    def get_rows(self, keys, mylist, clause=[]):
        indexes = []

        for key in keys:
            for i in range(len(self.colnames)):     # Gather the indexes in colnames that match key (ordered)
                if key == self.colnames[i] or key == "*":
                    indexes.append(i)

        lst = []
        for row in mylist:
            tmp = []
            for i in range(len(indexes)):
                tmp.append(row[indexes[i]])
            lst.append(tuple(tmp))

        return lst

    def sql_sort(self, keys, clause=[], desc=False):
        indexes = []
        evalindex = 0
        for key in keys:
            for i in range(len(self.colnames)):  # Gather the indexes in colnames that match key (ordered)
                if key == self.colnames[i]:
                    indexes.append(i)

        if clause:
            for i in range(len(self.colnames)):
                if clause[0] == self.colnames[i]:
                    evalindex = i
            lst = []
            for row in self.rows:
                if eval(f"{row.data[evalindex]}{clause[1]}{clause[2]}"):
                    lst.append(list(row.data))  # Convert tuples in tbl.row to list, and then sort by multiple keys w itemgetter
        else:
            lst = []
            for row in self.rows:
                lst.append(list(row.data))

        if desc:
            lst.sort(key=operator.itemgetter(*indexes), reverse=True)     # Unpack indexes in item getter
        else:
            lst.sort(key=operator.itemgetter(*indexes))

        lst = [tuple(x) for x in lst]
        return lst

    def update(self, keys, clause=[]): # Function to update values in table when given sets of instructions (eg. SET grade = 3.0, piazza = 1.0)
        for i in keys:  # Remove commas and = from keys, so keys should be pairs of [col, const, ...]
            if i == "=" or i == ",":
                keys.remove(i)

        if not clause:
            for i in range(len(keys)):
                if i % 2 != 0:              # Lazy way to parse keys, don't need to compare the odd indexed keys,
                    continue                # because they're constants
                for x in range(len(self.colnames)):     # For every colname in key, iterate through colnames until match
                    if keys[i] == self.colnames[x]:
                        for row in self.rows:           # If match, iterate through every row, create a list copy of it,
                            tmp = list(row.data)        # change the row value for our match (x), to the next value in keys
                            tmp[x] = keys[i+1]          # (constant in keys[i+1]))
                            row.data = tuple(tmp)       # Re add it as a tuple

        # else:
        #     for i in range(len(keys)):
        #         if i % 2 != 0:
        #             continue
        #         for x in range(len(self.colnames)):
        #             if clause[0] == self.colnames[x]:

    def delete(self, clause=[]):
        if clause:
            index = 0
            for i in range(len(self.colnames)):
                if self.colnames[i] == clause[0]:
                    index = i

            y = 0
            if clause[1] == "=":
                while y < len(self.rows):
                    tmp = self.rows[y].data[index]
                    if self.rows[y].data[index] == clause[2]:
                        self.rows.remove(self.rows[y])
                        continue
                    y += 1

            if clause[1] == ">":
                while y < len(self.rows):
                    tmp = self.rows[y].data[index]
                    if self.rows[y].data[index] > clause[2]:
                        self.rows.remove(self.rows[y])
                        continue
                    y += 1

            if clause[1] == "<":
                while y < len(self.rows):
                    tmp = self.rows[y].data[index]
                    if self.rows[y].data[index] < clause[2]:
                        self.rows.remove(self.rows[y])
                        continue
                    y += 1

            if clause[1] == "!=":
                while y < len(self.rows):
                    if self.rows[y].data[index] != clause[2]:
                        self.rows.remove(self.rows[y])
                        continue
                    y += 1

            if clause[1] == "IS NOT":
                while y < len(self.rows):
                    if self.rows[y].data[index] > clause[2]:
                        self.rows.remove(self.rows[y])
                        continue
                    y += 1
        else:
            self.rows = []


class Row(object):
    def __init__(self):
        self.data = ()

    def __init__(self, lst):
        self.data = tuple(lst)

    def __repr__(self):
        s = ''
        for i in range(len(self.data)):
            s += self.data[i] + " "
        return s


def collect_characters(query, allowed_characters):
    letters = []
    for letter in query:
        if letter not in allowed_characters:
            break
        letters.append(letter)
    return "".join(letters)


def remove_leading_whitespace(query, tokens):
    whitespace = collect_characters(query, string.whitespace)
    return query[len(whitespace):]


def remove_word(query, tokens):
    word = collect_characters(query,
                                    string.ascii_letters + "_" + string.digits + "." + "*")
    if word == "NULL":
        tokens.append(None)
    elif "." in word and word[word.find(".") + 1].isalpha():
        tokens.append(word)
    elif "." in word and word[word.find(".") + 1] == "*":
        tokens.append(word)
    elif "." in word:
        tokens.append(float(word))
    elif word.isdigit():
        tokens.append(int(word))
    else:
        tokens.append(word)
    return query[len(word):]


def remove_text(query, tokens):
    assert query[0] == "'"
    query = query[1:]
    newq = ""
    for i in range(len(query)):
        if i < len(query):
            if query[i] == "'" and query[i + 1] == "'":
                continue
            newq += query[i]

    text = newq[0:newq.find(",") - 1]
    if text[-1] == "'":
        text = text[:-1]
    if query[query.find(text) + len(text) + 1] == ")":
        query = query[query.find(text) + len(text) + 1:]
    else:
        query = query[query.find(","):]
    tokens.append(text)
    return query


def tokenize(query):
    tokens = []
    while query:
        old_query = query

        # TO DO - Add gathering clause "IS", "IS NOT", "NULL" etc.
        if query[0] in string.whitespace:
            query = remove_leading_whitespace(query, tokens)
            continue

        if query[0] in (string.ascii_letters + "_"):
            query = remove_word(query, tokens)
            continue

        if query[0] in '(),;="?':
            tokens.append(query[0])
            query = query[1:]
            continue

        if query[0] == "'":
            query = remove_text(query, tokens)
            continue

        # xtodo integers, floats, misc. query stuff (select * for example)
        if query[0] in (string.digits):
            query = remove_word(query, tokens)
            continue

        if query[0] == "*":
            tokens.append(query[0])
            query = query[1:]
            continue

        if query[0] in "><=":
            tokens.append(query[0])
            query = query[1:]

        if len(query) == len(old_query):
            raise AssertionError("Query didn't get shorter.")

    return tokens

class Connection(object):
    def __init__(self, filename):
        """
        Takes a filename, but doesn't do anything with it.
        (The filename will be used in a future project).
        """
        self.filename = filename
        self.db = Database()
        _ALL_DATABASES.append(self.db)

        bool = os.path.exists("./test.db")

        print(bool)

    def execute(self, statement):
        """
        Takes a SQL statement.
        Returns a list of tuples (empty unless select statement
        with rows to return).
        """

        tokens = tokenize(statement)

        if tokens[0] == "CREATE":
            tokstr = ""
            for elem in tokens:
                tokstr += str(elem) + " "

            for tbl in self.db.tables:
                if tbl.name == tokens[tokens.index("(") - 1]:
                    if "IF NOT EXISTS" in tokstr:
                        return
                    else:
                        raise AssertionError("Table already exists!")

            tbl = Table(tokens[2])      # Create a table with name (tokens[2] should always be name)
            data = []                   # Retreive data from query
            for i in range(4, tokens.index(')')):       # Should add a row to table
                if tokens[i] == ',':
                    continue
                data.append(tokens[i])
            tbl.set_types(data)
            self.db.add_table(tbl)  # Add table to DB

        if tokens[0] == "DROP":
            tokstr = ""
            for elem in tokens:
                tokstr += str(elem) + " "

            for tbl in self.db.tables:
                if tbl.name == tokens[tokens.index("(") - 1]:
                    if "IF EXISTS" in tokstr:
                        return
                    else:
                        raise AssertionError("Table doesn't exist!")

        if tokens[0] == "INSERT":
            tbl = self.db.get_table(tokens[2])
            cols = []
            if tokens[3] == "(":
                cols = []
                for i in range(4, tokens.index(")")):
                    if tokens[i] == ",":
                        continue
                    cols.append(tokens[i])

            data = []
            for i in range(tokens.index("VALUES") + 2, tokens.index(';') - 1):       # This code gathers tokens, cleans them up
                if tokens[i] == ',':                        # and puts each tuple of data into a list to be added to tbl
                    continue
                data.append(tokens[i])

            temp = []
            x = []
            for elem in data:
                if elem == "(":
                    continue
                if elem == ")":
                    x.append(temp)
                    temp = []
                    continue
                temp.append(elem)
            x.append(temp)

            data = x
            for elem in data:
                tbl.add_row(elem, cols)

        if tokens[0] == "SELECT":
            desc = False
            master = tokens[tokens.index("FROM") + 1]
            newtokens = []
            for token in tokens:
                if master in str(token):
                    newtokens.append(token[token.find(".")+1:])
                else:
                    newtokens.append(token)

            tokens = newtokens

            if 'DESC' not in tokens:
                ordering = tokens[tokens.index("BY") + 1: None]  ## ORDER BY
            else:
                ordering = tokens[tokens.index("BY") + 1:tokens.index("DESC")]
                desc = True

            if "WHERE" in newtokens:
                clause = newtokens[newtokens.index("WHERE") + 1:newtokens.index("ORDER")]
            else:
                clause = []

            for elem in ordering:
                if elem == ',' or elem == ';':  # Grab ordering elements, remove commas and semicolon
                    ordering.remove(elem)

            if tokens[1] == "*" and tokens[2] == "FROM":
                tbl = self.db.get_table(tokens[3])
                lst = tbl.sql_sort(ordering, clause, desc)
            else:
                tbl = self.db.get_table(tokens[tokens.index("FROM") + 1])       # Multiple select
                lst = tbl.sql_sort(ordering, clause, desc)

                if "MAX" in tokens:
                    tmp = []
                    max = -999999
                    col = tokens[3]
                    for i in range(len(tbl.colnames)):
                        if col == tbl.colnames[i]:
                            index = i
                    for row in tbl.rows:
                        if row.data[index] > max:
                            max = row.data[index]
                    tup = tuple()
                    tup = tup + (max,)
                    tmp.append(tup)
                    return tmp

                if "MIN" in tokens:
                    tmp = []
                    max = 999999
                    col = tokens[3]
                    for i in range(len(tbl.colnames)):
                        if col == tbl.colnames[i]:
                            index = i
                    for row in tbl.rows:
                        if row.data[index] < max:
                            max = row.data[index]
                    tup = tuple()
                    tup = tup + (max,)
                    tmp.append(tup)
                    return tmp


                cols = []
                for i in range(1, tokens.index("FROM")):                    # Grab table, select columns
                    if tokens[i] == ',':
                        continue
                    cols.append(tokens[i])

                lst = tbl.get_rows(cols, lst)

            return lst

        if tokens[0] == "UPDATE":
            tbl = self.db.get_table(tokens[1])
            if "WHERE" not in tokens:
                keys = tokens[tokens.index("SET") + 1:len(tokens)-1]
            else:
                keys = tokens[tokens.index("SET") + 1:tokens.index("WHERE")]
                clause = tokens[tokens.index("WHERE") + 1:tokens.index(";")]
            tbl.update(keys, clause)

        if tokens[0] == "DELETE":
            tbl = self.db.get_table(tokens[2])
            if "WHERE" in tokens:
                clause = tokens[tokens.index("WHERE") + 1:tokens.index(";")]
                tbl.delete(clause)
            else:
                tbl.delete()

        return []

    def executemany(self, statement, parameters):
        self.execute(statement)

        tokens = tokenize(statement)
        tbl = self.db.get_table(tokens[2])
        for param in parameters:
            for row in tbl.rows:
                tmp = list(row.data)
                for i in range(len(param)):
                    tmp[i] = param[i]
                tbl.add_row(tmp)
                break
        tbl.rows.remove(tbl.rows[0])

    def close(self):
        """
        Database should be written to a file in JSON format
        and the database should be closed.
        """
        db = self.db
        db.name = self.filename
        jsonStr = db.toJSON()
        with open(db.name, "w") as file:
            file.write(jsonStr)

def connect(filename):
    """
    Creates a Connection object with the given filename
    """
    return Connection(filename)


conn = Connection("test.db")
# conn.execute("CREATE TABLE students (name TEXT, grade REAL);")
# conn.execute("INSERT INTO students VALUES ('James', 2.4), ('Yaxin', 3.5), ('Li', 3.7), ('Charles', 4.0);")
# conn.execute("SELECT name FROM students WHERE grade > 3.0 ORDER BY name;")
# conn.close()
