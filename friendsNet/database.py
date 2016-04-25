'''
Provides the database API to access the friendsNet persistent data.
'''
import time, sqlite3, os

DEFAULT_DB_PATH = "db/friendsNet.db"
DEFAULT_SCHEMA = "db/friendsNet_schema_db.sql"
DEFAULT_DATA_DUMP = "db/friendsNet_data_db.sql"

class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    engine = Engine()
    con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at "db/friendsNet.db"
    '''
    def __init__(self, db_path=None):
        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH
            
    def connect(self):
        '''
        Creates a connection to the database.
    
        :return: A Connection instance
        :rtype: Connection
    
        '''
        return Connection(self.db_path)
    
    def remove_database(self):
        '''
        Removes the database file from the filesystem.
    
        '''
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema.
    
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreign keys support
        with con:
            cur = con.cursor()
            cur.execute(keys_on)
            cur.execute("DELETE FROM users_credentials")
            cur.execute("DELETE FROM media_items")
            cur.execute("DELETE FROM groups")
            cur.execute("DELETE FROM conversations")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(user_id) FROM users_credentials) WHERE name='users_credentials'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(status_id) FROM statuses) WHERE name='statuses'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(rate_id) FROM rates) WHERE name='rates'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(message_id) FROM messages) WHERE name='messages'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(media_item_id) FROM media_items) WHERE name='media_items'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(group_id) FROM groups) WHERE name='groups'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(friendship_id) FROM friendships) WHERE name='friendships'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(conversation_id) FROM conversations) WHERE name='conversations'")
            cur.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(comment_id) FROM comments) WHERE name='comments'")

    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then "db/friendsNet_schema_db.sql" is utilized.

        '''
        if schema is None:
            schema = DEFAULT_SCHEMA
            with open(schema) as f:
                sql = f.read()
                con = sqlite3.connect(self.db_path)
                cur = con.cursor()
                cur.executescript(sql)
                
    def populate_tables(self, dump=None):
        ''''       
        Populate programmatically the tables from a dump file.
            
        :param dump:  path to the .sql dump file. If this parmeter is
        None, then "db/friendsNet_data_db.sql" is utilized.
            
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
            with open (dump) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)


class Connection(object):
    '''
    API to access the friendsNet database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)
        
    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()
            
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        cur = self.con.cursor()
        try:
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            raise excp
        finally:
            cur.close()
        return is_activated
    
    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.
    
        :return: ``True`` if operation succeed and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.
    
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        result = False
        cur = self.con.cursor()
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            #execute the pragma command, ON
            cur.execute(keys_on)
            result = True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
        finally:
            cur.close()
        return result
        
    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        result = False
        cur = self.con.cursor()
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            #execute the pragma command, OFF
            cur.execute(keys_on)
            result = True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
        finally:
            cur.close()        
       	return result
            
    
    #HELPERS
    def _create_user_credentials_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``user_id``: user's id (int)
            * ``user_email``: user's email address
            * ``user_password``: user's password
            * ``user_registration_time``: time of user's registration on platform (long)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        user_id = row["user_id"]
        user_email = row["email"]
        user_password = row["password"]
        user_registration_time = row["registration_time"]
        
        user_credentials_object = {"user_id" : user_id, "user_email" : user_email, "user_password" : user_password, "user_registration_time" : user_registration_time}
        return user_credentials_object
    
    def _create_user_profile_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``user_id``: user's id (int)
            * ``first_name``: user's first name
            * ``middle_name``: user's middle name
            * ``surname``: user's surname
            * ``prof_picture_id``: user's profile picture id (int)
            * ``age``: user's age (int)
            * ``gender``: user's gender (int) (0 = male, 1 = female, 2 = unspecified)
              the user registred on the platform.

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        user_id = row["user_id"]
        first_name = row["first_name"]
        middle_name = row["middle_name"]
        surname = row["surname"]
        prof_picture_id = row["prof_picture_id"]
        age = row["age"]
        gender = row["gender"]
        
        user_profile_object = {"user_id" : user_id, "first_name" : first_name, "middle_name" : middle_name, "surname" : surname, "prof_picture_id" : prof_picture_id, "age" : age, "gender" : gender}
        return user_profile_object
    
    def _create_status_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``status_id``: status id (int)
            * ``creator_id``: status creator's id (int)
            * ``content``: status content
            * ``creation_time``: time of status creation (long)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        status_id = row["status_id"]
        creator_id = row["creator_id"]
        content = row["content"]
        creation_time = row["creation_time"]
        
        status_object = {"status_id" : status_id, "creator_id" : creator_id, "content" : content, "creation_time" : creation_time}
        return status_object
    
    def _create_rate_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``rate_id``: rate id (int)
            * ``status_id``: status to which the rate belongs to (int)
            * ``user_id``: rater id (int)
            * ``rate``: value of the rate (int) (0 <= rate <= 5)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        rate_id = row["rate_id"]
        status_id = row["status_id"]
        user_id = row["user_id"]
        rate = row["rate"]
        
        rate_object = {"rate_id" : rate_id, "status_id" : status_id, "user_id" : user_id, "rate" : rate}
        return rate_object
    
    def _create_message_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``message_id``: message id (int)
            * ``conversation_id``: conversation id which rate belongs to (int)
            * ``sender``: sender id (int)
            * ``content``: content of the message
            * ``time_sent``: time which message was sent (int)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        message_id = row["message_id"]
        conversation_id = row["conversation_id"]
        sender_id = row["sender_id"]
        content = row["content"]
        time_sent = row["time_sent"]
        
        message_object = {"message_id" : message_id, "conversation_id" : conversation_id, "sender_id" : sender_id, "content" : content, "time_sent" : time_sent}
        return message_object
    
    def _create_media_item_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``media_item_id``: media id (int)
            * ``media_item_type``: media type (int) (0 = photo, 1 = video)
            * ``url``: url that uniquely identifies the media element
            * ``description``: media textual description

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        media_item_id = row["media_item_id"]
        media_item_type = row["media_item_type"]
        url = row["url"]
        description = row["description"]
        
        media_item_object = {"media_item_id" : media_item_id, "media_item_type" : media_item_type, "url" : url, "description" : description}
        return media_item_object
    
    def _create_group_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``group_id``: group id (int)
            * ``name``: group name
            * ``prof_picture_id``: group profile picture id (int)
            * ``privacy_level``: privacy level of the group (int) (0 = secret, 1 = private, 2 = public)
            * ``description``: group description

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        group_id = row["group_id"]
        name = row["name"]
        prof_picture_id = row["prof_picture_id"]
        privacy_level = row["privacy_level"]
        description = row["description"]
        
        group_object = {"group_id" : group_id, "name" : name, "prof_picture_id" : prof_picture_id, "privacy_level" : privacy_level, "description" : description}
        return group_object
    
    def _create_members_list_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``group_id``: group id which the member belongs to (int)
            * ``user_id``: member id (int)
            * ``administrator``: type of member (int) (0 = user, 1 = administrator)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        group_id = row["group_id"]
        user_id = row["user_id"]
        user_type = row["administrator"]
        
        members_list_object = {"group_id" : group_id, "user_id" : user_id, "administrator" : user_type}
        return members_list_object
    
    def _create_group_request_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.
            
        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:
            
        * ``group_id``: group id (int)
        * ``user_id``: user id (int)
            
        Note that all values in the returned dictionary are string unless otherwise stated.
        
        '''
        group_id = row["group_id"]
        user_id = row["user_id"]
        
        request_object = {"group_id" : group_id, "user_id" : user_id}
        return request_object
    
    def _create_friendship_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``frienship_id``: friendship id (int)
            * ``user1_id``: friend-1 id (int)
            * ``user2_id``: friend-2 id (int)
            * ``friendship_status``: status of friendship (int) (0 = pending, 1 = accepted)
            * ``friendship_start``: time in which frienship request has been accepted (long)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        friendship_id = row["friendship_id"]
        user1_id = row["user1_id"]
        user2_id = row["user2_id"]
        friendship_status = row["friendship_status"]
        friendship_start = row["friendship_start"]
        
        friendship_object = {"friendship_id" : friendship_id, "user1_id" : user1_id, "user2_id" : user2_id, "friendship_status" : friendship_status, "friendship_start" : friendship_start}
        return friendship_object
    
    def _create_conversation_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``conversation_id``: conversation id (int)
            * ``user1_id``: user-1 id (int)
            * ``user2_id``: user-2 id (int)
            * ``time_last_message``: time in which last message has been sent (long)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        conversation_id = row["conversation_id"]
        user1_id = row["user1_id"]
        user2_id = row["user2_id"]
        time_last_message = row["time_last_message"]
        
        conversation_object = {"conversation_id" : conversation_id, "user1_id" : user1_id, "user2_id" : user2_id, "time_last_message" : time_last_message}
        return conversation_object
    
    def _create_comment_object(self, row):
    	'''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``comment_id``: comment id (int)
            * ``status_id``: status which comment belongs to (int)
            * ``user_id``: commentor id (int)
            * ``content``: comment content
            * ``creation_time``: time in which comment has been created (long)

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        comment_id = row["comment_id"]
        status_id = row["status_id"]
        user_id = row["user_id"]
        content = row["content"]
        creation_time = row["creation_time"]
        
        comment_object = {"comment_id" : comment_id, "status_id" : status_id, "user_id" : user_id, "content" : content, "creation_time" : creation_time}
        return comment_object
    
    
    #API
    def create_user(self, values):
    	'''
        Insert a new user in the database.

        :param values: dictionary containing values specified in py:_create_user_profile_object:

        -email must be unique;
        -password must be at least 8 charaters long;
        -middle_name can be null;
        -prof_picture_id must be null;

        :return: id of just created user (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        email = values["email"]
        password = values["password"]
        first_name = values["first_name"]
        middle_name = values.get("middle_name", None)
        profile_picture_id = values.get("prof_picture_id", None)
        surname = values["surname"]
        age = values["age"]
        gender = values["gender"]
        reg_time = long(round(time.time() * 1000))
        
        query1 = "INSERT INTO USERS_CREDENTIALS VALUES (NULL, ?, ?, ?)"
        query1_parameters = (email, password, reg_time)
        
        user_id = None        
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query1, query1_parameters)
            query2 = "INSERT INTO USERS_PROFILES VALUES (?, ?, ?, ?, ?, ?, ?)"
            query2_parameters = (user_id, first_name, middle_name, surname, profile_picture_id, age, gender)
            cur.execute(query2, query2_parameters)
            self.con.commit()
            user_id = cur.lastrowid
        except sqlite3.IntegrityError, err:          #There could be a check error, for the email if it's not unique
            self.con.rollback()
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return user_id
    
    def create_media(self, values):                                 #Create a new media item, uploaded on the platform
        '''
        Insert a new media in the database.

        :param values: dictionary containing values specified in py:_create_media_item_object:

        -media_id must be null;
        -media_item_type must be either 0 or 1;
        -url must be unique;

        :return: id of just created media (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        media_type = values["media_type"]
        url = values["url"]
        description = values.get("description", None)
        
        query = "INSERT INTO MEDIA_ITEMS VALUES (NULL, ?, ?, ?)"
        query_parameters = (media_type, url, description)
        
        media_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                media_id = cur.lastrowid
                self.con.commit()
        except sqlite3.IntegrityError, err:          #There could be a check error, for the url if it's not unique
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return media_id
    
    def create_group(self, values):
        '''
        Insert a new group in the database.

        :param values: dictionary containing values specified in py:_create_group_object:

        -group_id must be null;
        -prof_picture_id must be null;
        -privacy_level must be included in [0, 2] range;
        -description can be null;

        :return: id of just created group (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        name = values["name"]
        prof_picture_id = values.get("prof_picture_id", None)
        privacy_level = values["privacy_level"]
        description = values.get("description", None)
        
        query = "INSERT INTO GROUPS VALUES (NULL, ?, ?, ?, ?)"
        query_parameters = (name, prof_picture_id, privacy_level, description)
        
        group_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                group_id = cur.lastrowid
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return group_id
    
    def add_member_to_group(self, group_id, user_id):
        '''
        Insert a new member for a group.

        :param group_id: group id (int)
        :param user_id: user id (int)

        -group_id must exist;
        -user_id must exist;
        -user_id must not be already present in the group

        :return: True if operation is completed successfully, False otherwise.

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        query = "INSERT INTO GROUPS_MEMBERS_LISTS VALUES (?, ?, ?)"
        user_type = 0
        query_parameters = (group_id, user_id, user_type)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                result = True
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return result
    
    def create_conversation(self, values):
        '''
        Insert a new conversation between two users.

        :param values: dictionary containing values specified in py:_create_conversation_object:

        -conversation_id must be null;
        -user1_id must exist;
        -user2_id must exist;
        -user1_id and user2_id (or viceversa) must be unique;
        -time_last_message must be null;

        :return: id of just created conversation (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        user1_id = values["user1_id"]
        user2_id = values["user2_id"]
        
        query1 = "SELECT conversation_id FROM CONVERSATIONS WHERE user2_id = ? AND user1_id = ?"        #Search if the same users in opposite order are present
        query1_parameters = (user1_id, user2_id)
        
        conversation_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        if cur.fetchone() is None:                  #If there is no conversation between the same users in the opposite way
            time_creation = long(round(time.time() * 1000))
        
            query2 = "INSERT INTO CONVERSATIONS VALUES (NULL, ?, ?, ?)"
            query2_parameters = (user1_id, user2_id, time_creation)
            try:
                cur.execute(query2, query2_parameters)
                if cur.lastrowid >= 1:
                    conversation_id = cur.lastrowid
                    self.con.commit()
            except sqlite3.IntegrityError, err:
                print "Error %s:" % err.args[0]
            finally:
                cur.close()
        return conversation_id

    def add_request_to_group(self, group_id, user_id):
        '''
        Add a new request to the queue of requests for the group.

        :param group_id: group for which user is sending the request (int)

        :param user_id: user who's making request to join the group (int)

        -user must not have already sent a request or must not be already a member of the group

        :return: true if the request is added to the requests queue, false otherwise
        '''
        query1 = "SELECT * FROM GROUPS_REQUESTS_LISTS WHERE group_id = ? AND user_id = ?"
        query1_parameters = (group_id, user_id)

        result = False

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        if cur.fetchone() is None:
            query2 = "SELECT * FROM GROUPS_MEMBERS_LISTS WHERE group_id = ? AND user_id = ?"
            query2_parameters = (group_id, user_id)
            cur.execute(query2, query2_parameters)
            if cur.fetchone() is None:
                query3 = "INSERT INTO GROUPS_REQUESTS_LISTS VALUES (?, ?)"
                query3_parameters = (group_id, user_id)
                try:
                    cur.execute(query3, query3_parameters)
                    if cur.rowcount >= 1:
                        result = True
                        self.con.commit()
                except sqlite3.IntegrityError, err:
                    print "Error %s:" % err.args[0]
                finally:
                    cur.close()
        return result
    
    def create_friendship(self, user1_id, user2_id):
        '''
        Insert a new frienship between two users.

        :param user1_id: first user who's becoming friend (int)
        :param user2_id: second user who's becoming friend (int)

        -user1_id must exist;
        -user2_id must exist;
        -user1_id and user2_id (or viceversa) must be unique;

        :return: id of just created friendship (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        query1 = "SELECT friendship_id FROM FRIENDSHIPS WHERE user1_id = ? AND user2_id = ?"              #Check if the same users are present in the opposite order
        query1_parameters = (user2_id, user1_id)
        
        friendship_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        if cur.fetchone() is None:
            friendship_status = 0
            
            query2 = "INSERT INTO FRIENDSHIPS VALUES (NULL, ?, ?, ?, NULL)"
            query2_parameters = (user1_id, user2_id, friendship_status)
            try:
                cur.execute(query2, query2_parameters)
                if cur.lastrowid >= 1:
                    friendship_id = cur.lastrowid
                    self.con.commit()
            except sqlite3.IntegrityError, err:
                print "Error %s:" % err.args[0]
            finally:
                cur.close()
        return friendship_id         
  
    def create_status(self, values, group_id=None):
        '''
        Insert a new status in the database. It can be posted by the member of a group.

        :param values: dictionary containing values specified in py:_create_status_object:
        :param group_id: id of the group in which the status is posted.

        -status_id must be null;
        -creation_time must be null;
        -creator_id must exist;
        -group_id can be null;

        :return: id of just created status (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        creator_id = values["creator_id"]
        content = values.get("content", None)
        creation_time = long(round(time.time() * 1000))
        
        status_id = None
        
        query1 = "INSERT INTO STATUSES VALUES (NULL, ?, ?, ?)"
        query1_parameters = (creator_id, content, creation_time)
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query1, query1_parameters)
            if cur.lastrowid >= 1:
                stat_id = cur.lastrowid #Not official variable because if next query fails, None must be returned
                
                if group_id is not None:
                    query2 = "INSERT INTO GROUPS_STATUSES_LISTS VALUES (?, ?)"
                    query2_parameters = (group_id, stat_id)
                    cur.execute(query2, query2_parameters)
                self.con.commit()
                status_id = stat_id
        except sqlite3.IntegrityError, err:
            self.con.rollback()
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return status_id
    
    def add_media_to_status(self, status_id, media_id):
        '''
        Attach a new media to a status.

        :param status_id: status id (int)
        :param media_id: media id (int)

        -status_id must exist;
        -media_id must exist;
        -(status_id, media_id) must be unique;

        :return: True if media is correctly attached to the status, False otherwise.

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        query = "INSERT INTO STATUSES_MEDIA_LISTS VALUES (?, ?)"
        query_parameters = (status_id, media_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.rowcount >= 1:
                result = True
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return result
    
    def add_tag_to_status(self, status_id, user_id):
        '''
        Insert a new tag for a status.

        :param status_id: status id (int)
        :param user_id: user id (int)

        -status_id must exist;
        -user_id must exist;
        -(status_id, user_id) must be unique;

        :return: True if tag is correctly attached to the status, False otherwise.

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        query = "INSERT INTO STATUSES_TAGS_LISTS VALUES (?, ?)"
        query_parameters = (status_id, user_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.rowcount >= 1:
                result = True
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return result
    
    def add_comment_to_status(self, status_id, values):
        '''
        Insert a new comment for a status.

        :param status_id: status id (int)
        :param values: dictionary containing values specified in py:_create_comment_object:

        -comment_id must be null;
        -user_id must exist;
        -content cannot be null;
        -creation_time must be null;

        :return: id of just created comment.

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''   
        commentor_id = values["user_id"]
        content = values["content"]
        creation_time = long(round(time.time() * 1000))
	
        comment_id = None
            
        query = "INSERT INTO COMMENTS VALUES (NULL, ?, ?, ?, ?)"
        query_parameters = (status_id, commentor_id, content, creation_time)
	
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()	
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                comment_id = cur.lastrowid
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return comment_id
    
    def add_rate_to_status(self, status_id, values):
        '''
        Insert a new rate for a status.

        :param status_id: status id (int)
        :param values: dictionary containing values specified in py:_create_rate_object:

        -rate_id must be null;
        -user_id must exist;
        -rate must be included in range [0, 5];

        :return: id of just created rate.

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        rater_id = values["user_id"]
        rate = values["rate"]
	
        rate_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()        
        query = "INSERT INTO RATES VALUES (NULL, ?, ?, ?)"
        query_parameters = (status_id, rater_id, rate)
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                self.con.commit()
                rate_id = cur.lastrowid
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return rate_id
    
    #values contains the values for message table and and array of media to attach
    def create_message(self, values):
        '''
        Create a new message for a conversation.

        :param values: dictionary containing values specified in py:_create_message_object

        -message_id must be null;
        -conversation_id must exist;
        -sender_id must exist;
        -time_sent must be null
        -content must exist

        :return: id of just created message (int).

        :raises IntegrityError: if one of conditions above is not respected

        Note that all values in the returned dictionary are string unless otherwise stated.

        '''
        conversation_id = values["conversation_id"]
        sender_id = values["sender_id"]
        content = values["content"]
        time_creation = long(round(time.time() * 1000))
        
        message_id = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        query = "INSERT INTO MESSAGES VALUES (NULL, ?, ?, ?, ?)"
        query_parameters = (conversation_id, sender_id, content, time_creation)
        try:
            cur.execute(query, query_parameters)
            if cur.lastrowid >= 1:
                message_id = cur.lastrowid
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return message_id
                        
        
    
    #Method used to authenticate users
    def get_user_id(self, email, password):                         #Get the user id given email and password (used for authentication)
        '''
        Get the user given email and password, if any.

        :param email: searched user's email
        :param password: searched user's password

        :return: user id (int) or None if nothing is found

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT user_id FROM USERS_CREDENTIALS WHERE email = ? and password = ?"
        query_parameters = (email, password)
        
        user_id = None        
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            user_id = row["user_id"]
        cur.close()
        return user_id

    def is_email_existing(self, email):
        '''
        Returns true if there is already a user with the email.

        :param email: searched email

        :return: true if email is already associated to a user, false otherwise
        '''
        query = "SELECT user_id FROM USERS_CREDENTIALS where email = ?"
        query_parameters = (email,)

        result = False

        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        result = (row is not None)
        cur.close()
        return result

    def search_user(self, name, surname):
        '''
        Get the users that match the search parameters.
        :param name: the name of the user
        :param surname: the surname of the user

        :return: array of users in dictionary format as declared in :py:_create_user_profile_object or None if nothing is found
        '''
        query = "SELECT * FROM USERS_PROFILES WHERE first_name LIKE ? AND surname LIKE ?"
        query_parameters = ('%'+name+'%', '%'+surname+'%')

        users = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            for row in rows:
                if users is None:
                    users = []
                user_profile_object = self._create_user_profile_object(row)
                users.append(user_profile_object)
        cur.close()
        return users

    
    def get_user_information(self, user_id):                       #Get all user profile information given user's id
        '''
        Get the user information given his id

        :param user_id: searched user's id (int)

        :return: user in dictionary format as declared in :py:_create_user_profile_object or None if nothing is found

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM USERS_PROFILES WHERE user_id = ?"
        query_parameters = (user_id,)
        
        user = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            user = self._create_user_profile_object(row)
        cur.close()
        return user

    def get_comment(self, comment_id):
        '''
        Get all information about a comment
        
        :param comment_id: searched comment id (int)
        
        :return: comment in dictionary format as declared in :py:_create_comment_object or None if nothing is found
        
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM COMMENTS WHERE comment_id = ?"
        query_parameters = (comment_id,)
    
        comment = None
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            comment = self._create_comment_object(row)
        cur.close()
        return comment
            
    def get_rate(self, rate_id):
        '''
        Get all information about a rate
        
        :param rate_id: searched rate id (int)
        
        :return: rate in dictionary format as declared in :py:_create_rate_object or None if nothing is found
        
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM RATES WHERE rate_id = ?"
        query_parameters = (rate_id,)
        
        rate = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            rate = self._create_rate_object(row)
        cur.close()
        return rate

    def get_status(self, status_id):
        '''
        Get all information about a status
        
        :param status_id: searched status id (int)
        
        :return: status in dictionary format as declared in :py_create_status_object or None if nothing is found
        
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM STATUSES WHERE status_id = ?"
        query_parameters = (status_id,)
    
        status = None
    
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            status = self._create_status_object(row)
        cur.close()
        return status
            
    def get_friendship(self, friendship_id):
        '''
        Get all information about a friendship
            
        :param friendship_id: searched friendship id (int)
            
        :return: friendship in dictionary format as declared in :py_create_friendship_object or None if nothing is found
            
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM FRIENDSHIPS WHERE friendship_id = ?"
        query_parameters = (friendship_id,)
        
        friendship = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            friendship = self._create_friendship_object(row)
        cur.close()
        return friendship
            
    def get_media_item(self, media_id):
        '''
        Get all information about a media item
        
        :param media_id: searched media id (int)
        
        :return: media_item in dictionary format as declared in :py_create_media_item_object or None if nothing is found
        
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM MEDIA_ITEMS WHERE media_item_id = ?"
        query_parameters = (media_id,)
        
        media = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            media = self._create_media_item_object(row)
        cur.close()
        return media

    def get_last_media_item_id(self):
        '''
        Get id of last media uploaded onto the system

        :return: the id (int) of the last media item uploaded onto the system.
        '''
        last_media_id = 0

        query = "SELECT media_item_id FROM MEDIA_ITEMS ORDER BY media_item_id DESC LIMIT 1"
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query)
        row = cur.fetchone()

        if row is not None:
            last_media_id = row["media_item_id"]
        cur.close()
        return last_media_id
    def get_conversation(self, conversation_id):
        '''
        Get all information about a conversation
            
        :param conversation_id: searched conversation id (int)
        
        :return: conversation in dictionary format as declared in :py_create_conversation_object or None if nothing is found
            
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM CONVERSATIONS WHERE conversation_id = ?"
        query_parameters = (conversation_id,)
        
        conversation = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            conversation = self._create_conversation_object(row)
        cur.close()
        return conversation

    def get_information_for_group(self, group_id):
        '''
        Get the group information given its id

        :param group_id: searched group id (int)

        :return: group in dictionary format as declared in :py:_create_group_object or None if nothing is found

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM GROUPS WHERE group_id = ?"
        query_parameters = (group_id,)
        
        group = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        row = cur.fetchone()
        if row is not None:
            group = self._create_group_object(row)
        cur.close()
        return group
    
    def get_members_for_group(self, group_id):
        '''
        Get the member of the searched group

        :param group_id: searched group id (int)

        :return: array of memberships in dictionary format as declared in :py:_create_members_list_object or None if nothing is found

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM GROUPS_MEMBERS_LISTS WHERE group_id = ?"
        query_parameters = (group_id,)
        
        users = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if users is None:
                    users = []
                members_list_object = self._create_members_list_object(row)
                users.append(members_list_object)
        cur.close()
        return users
    
    def get_requests_for_group(self, group_id):
        '''
        Get the requests of the searched group

        :param group_id: searched group id (int)

        :return: array of requests in dictionary format as declared in :py:_create_group_request_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM GROUPS_REQUESTS_LISTS WHERE group_id = ?"
        query_parameters = (group_id,)
        
        requests = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if requests is None:
                    requests = []
                request_object = self._create_group_request_object(row)
                requests.append(request_object)
        cur.close()
        return requests
    
    def get_messages_for_conversation(self, conversation_id):
        '''
        Get the messages of the searched conversation.

        :param conversation_id: searched conversation id (int)

        :return: array of messages in dictionary format as declared in :py:_create_message_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM MESSAGES WHERE conversation_id = ? ORDER BY time_sent DESC"
        query_parameters = (conversation_id,)
        
        messages = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if messages is None:
                    messages = []
                message_object = self._create_message_object(row)
                messages.append(message_object)
        cur.close()
        return messages
    
    def get_friendships_for_user(self, user_id):
        '''
        Get the frienships of the searched user

        :param user_id: searched user id (int)

        :return: array of friendships in dictionary format as declared in :py:_create_friendship_object or None if nothing is found
        They are ordered from the most recent to the least recent one, before accepted ones and then not accepted ones.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM FRIENDSHIPS WHERE user1_id = ? OR user2_id = ? ORDER BY friendship_start DESC"
        query_parameters = (user_id, user_id)
        
        friendships = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()        
        if rows is not None:
            for row in rows:
                if friendships is None:
                    friendships = []
                friendship_object = self._create_friendship_object(row)
                friendships.append(friendship_object)
        cur.close()
        return friendships
    
    def get_statuses_for_user(self, user_id):
        '''
        Get the statuses of the searched user

        :param user_id: searched user id (int)

        :return: array of statuses in dictionary format as declared in :py:_create_status_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM STATUSES WHERE creator_id = ? ORDER BY creation_time DESC"
        query_parameters = (user_id,)
        
        statuses = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if statuses is None:
                    statuses = []
                status_object = self._create_status_object(row)
                statuses.append(status_object)
        cur.close()
        return statuses
    
    def get_statuses_for_group(self, group_id):
        '''
        Get the statuses of the searched group

        :param group_id: searched group id (int)

        :return: array of statuses in dictionary format as declared in :py:_create_status_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query1 = "SELECT status_id FROM GROUPS_STATUSES_LISTS WHERE group_id = ?"
        query1_parameters = (group_id,)
        
        statuses = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            query2 = "SELECT * FROM STATUSES "
            query2_parameters = ()
            for i in range(0, len(rows)):
                if i == 0:
                    query2 += "WHERE "
                status_id = rows[i]["status_id"]
                query2 += "status_id = ? OR "
                query2_parameters += (status_id,)
                query2 = query2[:-3] + "ORDER BY status_id DESC"
                cur.execute(query2, query2_parameters)
                results = cur.fetchall()
                if results is not None:
                    for result in results:
                        if statuses is None:
                            statuses = []
                    status_object = self._create_status_object(result)
                    statuses.append(status_object)
        cur.close()
        return statuses

    def get_media_for_status(self, status_id):
        '''
        Get the media attached to the searched status.

        :param status_id: searched status id (int)

        :return: array of media in dictionary format as declared in :py:_create_media_item_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query1 = "SELECT media_item_id FROM STATUSES_MEDIA_LISTS WHERE status_id = ?"
        query1_parameters = (status_id,)
        
        media = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            query2 = "SELECT * FROM MEDIA_ITEMS "
            query2_parameters = ()
            for i in range(0, len(rows)):
                if i == 0:
                    query2 += "WHERE "
                media_id = rows[i]["media_item_id"]
                query2 += "media_item_id = ? OR "
                query2_parameters += (media_id,)
                query2 = query2[:-3]
                cur.execute(query2, query2_parameters)
                results = cur.fetchall()
                if results is not None:
                    for result in results:
                        if media is None:
                            media = []
                    media_object = self._create_media_item_object(result)
                    media.append(media_object)
        cur.close()
        return media
    
    def get_tagged_users_for_status(self, status_id):
        '''
        Get the tags of the searched status.

        :param status_id: searched user id (int)

        :return: array of users in dictionary format as declared in :py:_create_user_profile_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query1 = "SELECT user_id FROM STATUSES_TAGS_LISTS WHERE status_id = ?"
        query1_parameters = (status_id,)
        
        tags = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            query2 = "SELECT * FROM USERS_PROFILES "
            query2_parameters = ()
            for i in range(0, len(rows)):
                if i == 0:
                    query2 += "WHERE "
                user_id = rows[i]["user_id"]
                query2 += "user_id = ? OR "
                query2_parameters += (user_id,)
            query2 = query2[:-3]
            cur.execute(query2, query2_parameters)
            results = cur.fetchall()
            if results is not None:
                for result in results:
                    if tags is None:
                        tags = []
                    user_object = self._create_user_profile_object(result)
                    tags.append(user_object)
        cur.close()
        return tags
    
    def get_comments_for_status(self, status_id):
        '''
        Get the comments for the searched status

        :param status_id: searched status id (int)

        :return: array of comments in dictionary format as declared in :py:_create_comment_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM COMMENTS WHERE status_id = ? ORDER BY creation_time DESC"
        query_parameters = (status_id,)
	
        comments = None
	
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()	
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            for row in rows:
                if comments is None:
                    comments = []
                comment_object = self._create_comment_object(row)
                comments.append(comment_object)
        cur.close()
        return comments
    
    def get_rates_for_status(self, status_id):
        '''
        Get the rates for the searched status

        :param status_id: searched status id (int)

        :return: array of rates in dictionary format as declared in :py:_create_rate_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''      
        query = "SELECT * FROM RATES WHERE status_id = ?"
        query_parameters = (status_id,)
	
        rates = None
	
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()	
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            for row in rows:
                if rates is None:
                    rates = []
                rate_object = self._create_rate_object(row)
                rates.append(rate_object)
        cur.close()
        return rates	
    
    def get_groups_for_user(self, user_id):
        '''
        Get the groups for which the search user is member

        :param user_id: searched user id (int)

        :return: array of memberships in dictionary format as declared in :py:_create_members_list_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM GROUPS_MEMBERS_LISTS WHERE user_id = ?"
        query_parameters = (user_id,)
        
        memberships = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if memberships is None:
                    memberships = []
                group_membership_object = self._create_members_list_object(row)
                memberships.append(group_membership_object)
        cur.close()
        return memberships
    
    def get_conversations_for_user(self, user_id):
        '''
        Get the conversations for the searched user

        :param user_id: searched user id (int)

        :return: array of conversations in dictionary format as declared in :py:_create_conversation_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM CONVERSATIONS WHERE user1_id = ? OR user2_id = ? ORDER BY time_last_message DESC"
        query_parameters = (user_id, user_id)
        
        conversations = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if conversations is None:
                    conversations = []
                conversation_object = self._create_conversation_object(row)
                conversations.append(conversation_object)
        cur.close()
        return conversations    
    
    def get_tagged_statuses_for_user(self, user_id):
        '''
        Get the status in which the searched user has been tagged

        :param user_id: searched user id (int)

        :return: array of statuses in dictionary format as declared in :py:_create_status_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query1 = "SELECT status_id FROM STATUSES_TAGS_LISTS WHERE user_id = ?"
        query1_parameters = (user_id,)
        
        statuses = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        rows = cur.fetchall()
        if rows is not None and len(rows) > 0:
            query2 = "SELECT * FROM STATUSES "
            query2_parameters = ()
            for i in range(0, len(rows)):
                if i == 0:
                    query2 += "WHERE "
                status_id = rows[i]["status_id"]
                query2 += "status_id = ? OR "
                query2_parameters += (status_id,)
            query2 = query2[:-3] + "ORDER BY status_id DESC"
            cur.execute(query2, query2_parameters)
            results = cur.fetchall()
            if results is not None:
                for result in results:
                    if statuses is None:
                        statuses = []
                    status_object = self._create_status_object(result)
                    statuses.append(status_object)
        cur.close()
        return statuses
    
    def get_comments_for_user(self, user_id):
        '''
        Get the comments the searched user has posted

        :param user_id: searched user id (int)

        :return: array of comments in dictionary format as declared in :py:_create_comment_object or None if nothing is found.
        They're ordered from the most recent to the least recent one.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM COMMENTS WHERE user_id = ? ORDER BY creation_time DESC"
        query_parameters = (user_id,)
        
        comments = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if comments is None:
                    comments = []
                comment_object = self._create_comment_object(row)
                comments.append(comment_object)
        cur.close()
        return comments
    
    def get_rates_for_user(self, user_id):
        '''
        Get the rates the searched user has given

        :param user_id: searched user id (int)

        :return: array of rates in dictionary format as declared in :py:_create_rate_object or None if nothing is found.

        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        query = "SELECT * FROM RATES WHERE user_id = ?"
        query_parameters = (user_id,)
                
        rates = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        rows = cur.fetchall()
        if rows is not None:
            for row in rows:
                if rates is None:
                    rates = []
                rate_object = self._create_rate_object(row)
                rates.append(rate_object)
        cur.close()
        return rates        
    
    def get_friends_statuses_for_user(self, user_id, limit_to = 100):
        '''
        Get (at most) the most 1000 recent statuses (from most to least recent) posted by a user's friends on his own profile (not in a group).
        
        :param user_id: The user id whose friends' last statuses are fetched (int).
        
        :param limit_to: The maximum number of statuses that can be returned. Default value is 100.  (int).
        
        -limit_to, if negative, means no limit
        
        :return: array of statuses in dictionary format as declared in :py:_create_status_object or None if nothing is found.
        
        Note that all values in the returned dictionary are string unless otherwise stated.
        '''
        user_friendships = self.get_friendships_for_user(user_id)	    #Get all the user's friends
        
        statuses = None
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str	    
        cur = self.con.cursor()	
        
        if user_friendships is not None and len(user_friendships) > 0:	    #If user has at least one friend or has sent/received a friendship request not yet accepted
            
            user_friendships = [friendship for friendship in user_friendships if friendship["friendship_status"] == 1] #Filter the result taking only the existing (accepted) friendships
            query = "SELECT statuses.status_id, statuses.creator_id, statuses.content, statuses.creation_time FROM STATUSES LEFT JOIN GROUPS_STATUSES_LISTS ON STATUSES.status_id = GROUPS_STATUSES_LISTS.status_id WHERE "
            query_parameters = ()
            for i in range(0, len(user_friendships)):
                if i == 0:
                    query += "("			#Add round parentesis in order to avoid logical operators problems since AND (later in query) has higher priority than OR, if any
                friendship = user_friendships[i]
                user1_id = friendship["user1_id"]
                user2_id = friendship["user2_id"]
                friend_id = user1_id if user2_id == user_id else user2_id	    #Take the id of the other user (not the user passed as parameter) in the friendship
                query += "statuses.creator_id = ? OR "
                query_parameters += (friend_id,)
                if i == len(user_friendships) -	1:	    #If it's the last loop iteration, then finalize the query (removing the "OR" put at every loop step)
                    query = query[:-4] + ") "
            if len(user_friendships) > 0:		    #If at least one condition has been added to the query
                query += "AND "
            query += "groups_statuses_lists.group_id IS NULL ORDER BY statuses.creation_time DESC LIMIT ?"	    #We exclude the statuses that have been posted in groups and set the upper limit to the number of results and the inverse order so that first ones are the most recent ones
            query_parameters += (limit_to,)
            cur.execute(query, query_parameters)
            rows = cur.fetchall()
            if rows is not None:
                for row in rows:
                    if statuses is None:
                        statuses = []
                    status_object = self._create_status_object(row)
                    statuses.append(status_object)
        cur.close()
        return statuses  
	 
    
    def update_user(self, user_id, values):                        #Update user's values (only the ones allowed)
        '''
        Update user information.

        :param user_id: id of user to update (int)

        :param values: dictionary containing as possible keys:
        *'password' to change password;
        *'first_name' to change first name;
        *'middle_name' to change middle name;
        *'surname' to change surname;
        *'prof_picture_id' to change id of profile picture (int);
        *'gender' to change gender (int);
        *'age' to change age (int);

        -password must be at least 8 charaters long;
        -prof_picture_id must exist;
        -gender must be included in range (0, 2)
	
        :return: True if element has been updated correctly, False otherwise.
        '''
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        
        result = self.get_user_information(user_id) is not None
        
        if values.get("password", None) is not None:
            result = False
            password = values["password"]
            del values["password"]
            try:
                query = "UPDATE USERS_CREDENTIALS SET password = ? WHERE user_id = ?"
                query_parameters = (password, user_id)
                cur.execute(query, query_parameters)
                if cur.rowcount >= 1:
                    result = True
            except sqlite3.IntegrityError, err:
                print "Error %s:" % err.args[0]
        
        if len(values) > 0:
            result = False
            query = "UPDATE USERS_PROFILES SET "
            query_parameters = ()
            
            for col_name, col_value in values.iteritems():
                query += "%s = ?," % (col_name)
                query_parameters = query_parameters + (col_value,)
            query = query[:-1] + " WHERE user_id = ?"
            query_parameters = query_parameters + (user_id,)
            
            try:
                cur.execute(query, query_parameters)
                if cur.rowcount >= 1:
                    self.con.commit()
                    result = True
            except sqlite3.IntegrityError, err:          #There could be a check error, for the genre of the person
                self.con.rollback()
                print "Error %s:" % err.args[0]
            finally:
                cur.close()
        return result
    
    def update_media_description(self, media_id, description):              #Update (or remove) a media description
        '''
        Update media description.
        
        :param media_id: id of  media element (int)
        :param description: new description for the media item
        
        :return: True if element has been updated correctly, False otherwise.
        '''	
        query = "UPDATE MEDIA_ITEMS SET description = ? WHERE media_item_id = ?"
        query_parameters = (description, media_id)
        
        result = False        
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            self.con.commit()
            result = True
        cur.close()
        return result
    
    def update_group(self, group_id, values):
	'''
	Update group details.

	:param group_id: id of group to update (int)
	
	:param values: dictionary containing as possible keys:
	*'prof_picture_id' to change id of profile picture (int);
    *'name' to change group name;
	*'privacy_level' to change privacy level (int);
	*'description' to change description;
	
	-privacy_level must be included in the range (0, 2)
	
	:return: True if element has been updated correctly, False otherwise.
	'''
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        
        result = False
        
        if len(values) > 0:
            query = "UPDATE GROUPS SET "
            query_parameters = ()
            
            for col_name, col_value in values.iteritems():
                query += "%s = ?," % (col_name)
                query_parameters = query_parameters + (col_value,)
            query = query[:-1] + "WHERE group_id = ?"
            query_parameters = query_parameters + (group_id,)
            
            try:
                cur.execute(query, query_parameters)
                if cur.rowcount >= 1:
                    self.con.commit()
                    result = True
            except sqlite3.IntegrityError, err:
                print "Error %s:" % err.args[0]
            finally:
                cur.close()
        return result
                
    def update_group_member(self, group_id, values):
	'''
	Update membership of a user (promote to administrator/demote to normal user) in a group.
	
	:param group_id: id of group to update (int)
		
	:param values: dictionary containing keys:
	*'user_id' id of user to update (int);
	*'administrator' new value for the membership (int);
	
	-user_id must identify a member user of the group;
	-administrator must be included in the range (0, 1)
		
	:return: True if element has been updated correctly, False otherwise.
	'''	
        user_id = values["user_id"]
        new_status = values["administrator"]

        query1 = "SELECT administrator FROM GROUPS_MEMBERS_LISTS WHERE group_id = ?"
        query1_parameters = (group_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query1, query1_parameters)
        row = cur.fetchone()
        if row is not None:
            administrator = row["administrator"]
            query2 = "UPDATE GROUPS_MEMBERS_LISTS SET administrator = ? WHERE group_id = ? AND user_id = ? AND administrator != ?"
            query2_parameters = (new_status, group_id, user_id, new_status)            
            try:
                cur.execute(query2, query2_parameters)
                if cur.rowcount >= 1:
                    self.con.commit()
                    result = True
            except sqlite3.IntegrityError, err:
                print "Error %s:" % err.args[0]
            finally:
                cur.close()
        return result
    
    def update_conversation(self, conversation_id, last_time):                    #only column that can be modified
	'''
	Modify time of last update for a conversation.
	
	:param conversation_id: id of conversation to update (int)
	
	:param last_time: new value to set to the conversation (int)
		
	:return: True if element has been updated correctly, False otherwise.
	'''	
        query = "UPDATE CONVERSATIONS SET time_last_message = ? WHERE conversation_id = ?"
        query_parameters = (last_time, conversation_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def update_status_content(self, status_id, content):
	'''
	Modify content of a status.
	
	:param status_id: id of status to update (int)
	
	:param content: new content for the status
	
	:return: True if element has been updated correctly, False otherwise.
	'''
        query = "UPDATE STATUSES SET content = ? WHERE status_id = ?"
        query_parameters = (content, status_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def update_comment_content(self, comment_id, content):
	'''
	Modify content of a comment.
	
	:param comment_id: id of comment to update (int)
	
	:param content: new content for the comment
	
	:return: True if element has been updated correctly, False otherwise.
	'''
        query = "UPDATE COMMENTS SET content = ? WHERE comment_id = ?"
        query_parameters = (content, comment_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def update_rate_value(self, rate_id, rate):
	'''
	Modify value of a rate.
	
	:param rate_id: id of rate to update (int)
	
	:param rate: new value for the rate
	
	:return: True if element has been updated correctly, False otherwise.
	'''	
        query = "UPDATE RATES SET rate = ? WHERE rate_id = ? AND rate != ?"
        query_parameters = (rate, rate_id, rate)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        try:
            cur.execute(query, query_parameters)
            if cur.rowcount >= 1:
                result = True
                self.con.commit()
        except sqlite3.IntegrityError, err:
            print "Error %s:" % err.args[0]
        finally:
            cur.close()
        return result
        
    
    def accept_friendship(self, friendship_id):
	'''
	Modify status of a friendship putting it to 'accepted' and filling the start time field.
	
	:param friendship_id: id of friendship to update (int)
	
	:return: True if element has been updated correctly, False otherwise.
	'''	
        friendship_start = long(round(time.time() * 1000))
        query = "UPDATE FRIENDSHIPS SET friendship_status = 1, friendship_start = ? WHERE friendship_id = ?"
        query_parameters = (friendship_start, friendship_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result      
                
    
    def delete_user(self, user_id):                             #Delete a user given his id
	'''
	Delete a user.
	
	:param user_id: id of user to delete (int)
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM USERS_CREDENTIALS WHERE user_id = ?"
        query_parameters = (user_id,)

        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_media_item(self, media_id):
	'''
	Delete a media.
	
	:param media_id: id of media to delete (int)
	
	:return: True if element has been deleted correctly, False otherwise.
	'''		
        query = "DELETE FROM MEDIA_ITEMS WHERE media_item_id = ?"
        query_parameters = (media_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result        
    
    def delete_group(self, group_id):
	'''
	Delete a group.
	
	:param group_id: id of group to delete (int)
	
	:return: True if element has been deleted correctly, False otherwise.
	'''		
        query = "DELETE FROM GROUPS WHERE group_id = ?"
        query_parameters = (group_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_member(self, group_id, user_id):
	'''
	Delete a member from a group.
	
	:param group_id: id of group from which the user must be deleted (int)
	
	:param user_id: id of user to delete (int)
	
	:return: True if element has been deleted correctly, False otherwise.
	'''		
        query = "DELETE FROM GROUPS_MEMBERS_LISTS WHERE group_id = ? AND user_id = ?"
        query_parameters = (group_id, user_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result        
    
    def delete_group_request(self, group_id, user_id):
	'''
	Delete a membership request from a group.
	
	:param group_id: id of group from which the request must be deleted (int)
	
	:param user_id: id of user whose request is (int)
	
	:return: True if element has been deleted correctly, False otherwise.
	'''		
        query = "DELETE FROM GROUPS_REQUESTS_LISTS WHERE group_id = ? AND user_id = ?"
        query_parameters = (group_id, user_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def accept_group_request(self, group_id, user_id):
	'''
	Accept a membership request for a group.
	
	:param group_id: id of group from which the request must be accepted (int)
	
	:param user_id: id of user whose request is (int)
	
	:return: True if element has been accepted correctly, False otherwise.
	'''
        query = "DELETE FROM GROUPS_REQUESTS_LISTS WHERE group_id = ? AND user_id = ?"
        query_parameters = (group_id, user_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = self.add_member_to_group(group_id, user_id)
            if result:
                self.con.commit()
        cur.close()
        return result
    
    def delete_conversation(self, conversation_id):
	'''
	Delete a conversation.
	
	:param conversations_id: id of conversation to delete.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM CONVERSATIONS WHERE conversation_id = ?"
        query_parameters = (conversation_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result     
    
    def delete_friendship(self, friendship_id):                                     #Delete both existing friendships and pending requests
	'''
	Delete a frienship.
	
	:param friendship_id: id of friendship to delete.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''
        query = "DELETE FROM FRIENDSHIPS WHERE friendship_id = ?"
        query_parameters = (friendship_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result 
    
    def delete_media_from_status(self, status_id, media_id):
	'''
	Delete a media from a status.
	
	:param status_id: id of status from which the media must be deleted.
	
	:param media_id: id of media to delete from the status
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM STATUSES_MEDIA_LISTS WHERE status_id = ? AND media_item_id = ?"
        query_parameters = (status_id, media_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_status(self, status_id):
	'''
	Delete a status.
	
	:param status_id: id of status to delete.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM STATUSES WHERE status_id = ?"
        query_parameters = (status_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_tag(self, status_id, user_id):
	'''
	Delete a tag from a status.
	
	:param user_id: user that must be untagged from the status.
	
	:param status_id: id of status for which tag must be removed.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM STATUSES_TAGS_LISTS WHERE status_id = ? AND user_id = ?"
        query_parameters = (status_id, user_id)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_comment(self, comment_id):
	'''
	Delete a comment.
	
	:param comment_id: id of comment to delete.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''	
        query = "DELETE FROM COMMENTS WHERE comment_id = ?"
        query_parameters = (comment_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result
    
    def delete_rate(self, rate_id):
	'''
	Delete a rate.
	
	:param rate_id: id of rate to delete.
	
	:return: True if element has been deleted correctly, False otherwise.
	'''
        query = "DELETE FROM RATES WHERE rate_id = ?"
        query_parameters = (rate_id,)
        
        result = False
        
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row 
        self.con.text_factory = str
        cur = self.con.cursor()
        cur.execute(query, query_parameters)
        if cur.rowcount >= 1:
            result = True
            self.con.commit()
        cur.close()
        return result