import sqlite3
import Logger
import copy


class DBInterface:

    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.db_connection: sqlite3.Connection = sqlite3.connect(self.db_path, 10)
        self.db_connection.row_factory = sqlite3.Row
        self.db_cursor: sqlite3.Cursor = self.db_connection.cursor()

    def manual_debug(self):
        sqlstring: str = """ SELECT *
                             FROM recipe_ingredients
                         """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            print(f'Error in manual debug' + ret[1])

        results = self.db_cursor.fetchall()
        for row in results:
            print(tuple(row))

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
        ret: tuple = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        # Creating recipe tables
        sqlstring = """ CREATE TABLE recipes (
                        recipe_id INTEGER PRIMARY KEY NOT NULL,
                        recipe_title STRING NOT NULL,
                        recipe_notes STRING NOT NULL)
                    """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return ret
        sqlstring = """ CREATE TABLE recipe_ingredients (
                        ingredient_id INTEGER PRIMARY KEY,
                        ingredient_name STRING NOT NULL,
                        ingredient_quantity REAL NOT NULL,
                        ingredient_unit_type STRING NOT NULL,
                        kroger_upc STRING NOT NULL,
                        kroger_quantity REAL NOT NULL,
                        recipe_id INT NOT NULL,
                        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id))
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
        ret: tuple = self._execute_query(sqlstring, (1,))
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
        ret: tuple = self._execute_query(sqlstring, (1,))
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

    def add_recipe(self, recipe: dict) -> tuple[int, dict]:
        """
        recipe:  {'recipe_title': str,
                  'recipe_notes': str,
                  'ingredients': {<ingredient1>: {'ingredient_quantity': float,
                                                 'ingredient_name': str,
                                                 'ingredient_unit_type': str,
                                                 'kroger_upc': str,
                                                 'kroger_quantity: float},
                                {<ingredient2>: {...} }
                                }
                 }
        :return: A deep copy of recipe + the recipe and ingredient ids.
                 'ingredients' dict is re-keyed to ingredient_id
        """
        # Adding recipe table entry
        recipe_title: str = recipe['recipe_title']
        recipe_notes: str = recipe['recipe_notes']
        sqlstring: str = """ INSERT INTO recipes (recipe_title, recipe_notes)
                             VALUES (?, ?)
                         """
        ret: tuple = self._execute_query(sqlstring, (recipe_title, recipe_notes))
        if ret[0] != 0:
            Logger.Logger.log_error(f'Error adding {recipe_title} to database --' + ret[1])
            print(f' Error adding new recipe {recipe_title} to the database')
            return -1, {'error_message': f'Error adding {recipe_title} to the database--' + ret[1]}
        new_recipe_id: int = self.db_cursor.lastrowid
        # Adding ingredient table entries
        for ingredient, details in recipe['ingredients'].items():
            sqlstring = """ INSERT INTO recipe_ingredients
                            (ingredient_name
                            ,ingredient_quantity
                            ,ingredient_unit_type
                            ,kroger_upc
                            ,kroger_quantity
                            ,recipe_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """
            ret = self._execute_query(sqlstring, (details['ingredient_name'],
                                                  details['ingredient_quantity'],
                                                  details['ingredient_unit_type'],
                                                  details['kroger_upc'],
                                                  details['kroger_quantity'],
                                                  new_recipe_id))
            if ret[0] != 0:
                Logger.Logger.log_error(f'Error adding ingredient {ingredient} --' + ret[1])
                print(f'Error adding ingredient {ingredient}')
                # Returning without commit
                self.db_connection.rollback()
                return -1, {'error_message': f'Error adding ingredient {ingredient}--' + ret[1]}
            # Preparing return data
            new_ingredient_id: int = self.db_cursor.lastrowid
            recipe['ingredients'][ingredient]['ingredient_id'] = new_ingredient_id
        # Finalizing
        self.db_connection.commit()
        # 'ingredients' dict needs re-keying
        # on ingredient_id
        ingredient_keys = list(recipe['ingredients'].keys())
        for key in ingredient_keys:
            ingredient_details: dict = recipe['ingredients'][key]
            ingredient_id: int = ingredient_details['ingredient_id']
            recipe['ingredients'][ingredient_id] = ingredient_details
            recipe['ingredients'].pop(key)
        new_recipe: dict = copy.deepcopy(recipe)
        new_recipe['recipe_id'] = new_recipe_id
        return 0, new_recipe

    def get_recipes(self) -> tuple[int, dict]:
        """
        Pulls all recipe data and returns it as nested dictionaries
        :return: [int: -1, {'error_message': <>}]
                    OR
                 [int: 0, {<recipe_id>:    {'recipe_id': <>,
                                            'recipe_title': <>,
                                            'recipe_notes': <>,
                                            'ingredients': { 'ingredient_id': {<ingredient_name>,
                                                                            'ingredient_id': int,
                                                                            'ingredient_quantity': float,
                                                                            'ingredient_unit_type': str,
                                                                            'kroger_upc': str,
                                                                            'kroger_quantity': float
                                                                            }, ... } } }
        """
        sqlstring: str = """ SELECT 
                             r.recipe_id
                             ,r.recipe_title
                             ,r.recipe_notes
                             ,ri.ingredient_id
                             ,ri.ingredient_name
                             ,ri.ingredient_quantity
                             ,ri.ingredient_unit_type
                             ,ri.kroger_upc
                             ,ri.kroger_quantity
                             FROM recipes r left join recipe_ingredients ri on r.recipe_id = ri.recipe_id
                             ORDER BY r.recipe_id
                         """
        ret: tuple = self._execute_query(sqlstring)
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        # Structuring data
        new_recipe: dict = {}
        recipes: dict = {}
        results = self.db_cursor.fetchall()
        for row in results:
            new_ingredient: dict = {}
            if row['recipe_id'] not in recipes:
                # Initializing recipe
                if len(recipes) > 0:
                    new_recipe = dict()
                new_recipe_id = row['recipe_id']
                recipes[new_recipe_id] = new_recipe
                new_recipe['recipe_id'] = row['recipe_id']
                new_recipe['recipe_title'] = row['recipe_title']
                new_recipe['recipe_notes'] = row['recipe_notes']
                new_recipe['ingredients'] = dict()
            # Adding ingredient info from current row
            ingredient_id = row['ingredient_id']
            new_ingredient['ingredient_id'] = ingredient_id
            new_ingredient['ingredient_name'] = row['ingredient_name']
            new_ingredient['ingredient_quantity'] = row['ingredient_quantity']
            new_ingredient['ingredient_unit_type'] = row['ingredient_unit_type']
            new_ingredient['kroger_upc'] = str(row['kroger_upc'])
            new_ingredient['kroger_quantity'] = (row['kroger_upc'])
            new_recipe['ingredients'][ingredient_id] = new_ingredient
        return 0, recipes

    def delete_recipe(self, recipe_id: int) -> tuple[int, dict]:
        """
        Remove the 'recipe_ingredients' and 'recipes' entries
        for the given recipe_id
        :return:
        """
        # Clearing recipe_ingredients table
        sqlstring: str = """ DELETE FROM recipe_ingredients 
                             WHERE recipe_id = (?)
                         """
        ret = self._execute_query(sqlstring, (recipe_id,))
        print(self.db_cursor.lastrowid)
        if ret[0] != 0:
            Logger.Logger.log_error(f'Error deleting recipe_ingredient entries' + ret[1])
            print(f'Error deleting recipe_ingredient entries:' + ret[1])
            return -1, {'error_message': ret[1]}
        # Clearing recipes table
        sqlstring = """ DELETE FROM recipes 
                        WHERE recipe_id = (?)
                    """
        ret = self._execute_query(sqlstring, (recipe_id,))
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        self.db_connection.commit()
        return 0, {'success_message': f'Deleted recipe {recipe_id}'}

    def add_ingredient(self, recipe_id: int, ingredient: dict) -> tuple[int, dict]:
        """
        Adds a new ingredient entry into the database
        :param recipe_id:
        :param ingredient:  {'ingredient_name': <>,
                            'ingredient_quantity': <>,
                             'ingredient_unit_type': <>,
                             'kroger_upc':  <>,
                             'kroger_quantity: <>}
         :returns: {'ingredient_id':
        """
        sqlstring: str = """ INSERT INTO recipe_ingredients 
                                (ingredient_name
                                ,ingredient_quantity
                                ,ingredient_unit_type
                                ,kroger_upc 
                                ,kroger_quantity
                                ,recipe_id)
                             VALUES (?, ?, ?, ?, ?, ?)
                         """
        ret = self._execute_query(sqlstring, (ingredient['ingredient_name'],
                                              ingredient['ingredient_quantity'],
                                              ingredient['ingredient_unit_type'],
                                              ingredient['kroger_upc'],
                                              ingredient['kroger_quantity'],
                                              recipe_id))
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        ingredient_id: int = self.db_cursor.lastrowid
        self.db_connection.commit()
        return 0, {'ingredient_id': ingredient_id}

    def delete_ingredient(self, ingredient_id) -> tuple[int, dict]:
        sqlstring: str = """ DELETE FROM recipe_ingredients
                             WHERE ingredient_id = (?)
                         """
        ret = self._execute_query(sqlstring, (ingredient_id,))
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        self.db_connection.commit()
        return 0, {}

    def retitle_recipe(self, recipe_id: int, new_title: str) -> tuple[int, dict]:
        sqlstring: str = """ UPDATE recipes
                             set recipe_title = (?)
                             WHERE recipe_id = (?)
                         """
        ret = self._execute_query(sqlstring, (new_title
                                              , recipe_id))
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        self.db_connection.commit()
        return 0, {}

    def update_notes(self, recipe_id: int, updated_notes: str) -> tuple[int, dict]:
        sqlstring: str = """ UPDATE recipes
                             SET recipe_notes = (?)
                             WHERE recipe_id = (?)
                         """
        ret = self._execute_query(sqlstring, (updated_notes, recipe_id))
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        self.db_connection.commit()
        return 0, {}

    def new_recipe(self) -> tuple[int, dict]:
        sqlstring: str = """ INSERT INTO recipes 
                                (recipe_title
                                ,recipe_notes)
                             VALUES
                                ('<New Recipe>'
                                ,'<Recipe Notes>')
                         """
        ret = self._execute_query(sqlstring)
        if ret[0] != 0:
            return -1, {'error_message': ret[1]}
        recipe_id: int = self.db_cursor.lastrowid
        self.db_connection.commit()
        return 0, {'recipe_id': recipe_id}


