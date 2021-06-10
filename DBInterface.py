import sqlite3


class DBInterface:

    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.db_connection: sqlite3.Connection = sqlite3.connect(self.db_path, 10)
        self.db_connection.row_factory = sqlite3.Row
        self.db_cursor: sqlite3.Cursor = self.db_connection.cursor()

    def _execute_query(self, sql_string: str
                       , parameters: tuple = None) -> tuple[int, str]:
        """
        Wrapper for cursor.execute
        """
        try:
            if parameters is None:
                self.db_cursor.execute(sql_string)
            else:
                self.db_cursor.execute(sql_string, parameters)
            return 0, 'Successfully executed query'
        except sqlite3.Error as e:
            return -1, str(e)

    def seed_db(self) -> tuple[int, str]:
        """
        Initializes a new database with the project's schema.
        Drops existing tables.

        :return: [0] == 0 upon success, -1 failure
                 [1] is success/failure message
        """
        # Clearing existing tables
        db_tables = [
            'api_token',
            'recipes',
            'recipe_steps',
            'recipe_ingredients'
        ]
        for table in db_tables:
            sqlstring = f""" DROP TABLE IF EXISTS {table} """
            ret = self._execute_query(sqlstring)
            if ret[0] != 0:
                return ret
        # Creating token table
        # Only one token row exists at a time. Reuses id 1
        sqlstring = """ CREATE TABLE api_token (
                        token_id INT PRIMARY KEY,
                        refresh_token STRING NOT NULL,
                        timestamp REAL NOT NULL)
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        # Creating recipe tables
        sqlstring = """ CREATE TABLE recipes (
                        recipe_id INT PRIMARY KEY,
                        recipe_title STRING NOT NULL,
                        recipe_notes STRING NOT NULL)
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        sqlstring = """ CREATE TABLE recipe_steps (
                        step_id INT PRIMARY KEY,
                        recipe_id INTEGER NOT NULL,
                        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id))
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        sqlstring = """ CREATE TABLE recipe_ingredients (
                        ingredient_id INT PRIMARY KEY,
                        ingredient_name STRING NOT NULL,
                        ingredient_quantity REAL NOT NULL,
                        ingredient_unit_type STRING NOT NULL,
                        kroger_upc STRING)
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret

        return 0, 'Successfully seeded DB'

    def retrieve_token(self) -> tuple[int, tuple]:
        """
        Pulls the refresh token + unix timestamp, if it exists
        :return: int: -1 upon query error.
                 tuple: Failure message
                 ||
                 int: 0, successfully retrieved a token
                 tuple: (str: refresh_token, float: unix_timestamp)
                 ||
                 int: 1, No token found
                 tuple: (None,)
        """
        sqlstring = """ SELECT * FROM api_token
                        WHERE token_id = (?)
                    """
        ret = self._execute_query(sqlstring, (1,))
        if ret[0] != 0:
            return ret[0], (ret[1],)
        resultrow: tuple = self.db_cursor.fetchone()
        if resultrow is None:
            return 1, (None,)
        refresh_token: str = resultrow[1]
        timestamp: float = resultrow[2]
        return 0, (refresh_token, timestamp)

    def update_token(self, refresh_token: str, unix_timestamp: float) -> tuple[int, str]:
        """
        Insert/replace the api_token row with the latest refresh_token
        :return:  (int: -1 upon failure, else0,
                   str: outcome message)
        """
        # Checking for an existing token
        sqlstring: str = """    SELECT token_id
                                FROM api_token
                                WHERE token_id = (?)
                         """
        ret = self._execute_query(sqlstring, (1,))
        if ret[0] != 0:
            return ret
        rowdata: tuple = self.db_cursor.fetchone()
        if rowdata is not None:
            # Deleting the existing entry
            sqlstring = """ DELETE FROM api_token
                            WHERE token_id = (?)
                        """
            ret = self._execute_query(sqlstring, (1,))
            if ret[0] != 0:
                return ret
        # Inserting latest token
        sqlstring = """ INSERT INTO api_token (token_id, refresh_token, timestamp)
                        VALUES (?, ?, ?)
                    """
        ret = self._execute_query(sqlstring, (1, refresh_token, unix_timestamp))
        if ret[0] != 0:
            return ret
        self.db_connection.commit()
        return 0, 'Successfully updated refresh token'
