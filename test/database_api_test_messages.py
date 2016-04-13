import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

mes1 = {"conversation_id" : 1, "sender_id" : 1, "content" : "gedtvjdghosdvnht78gedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht7gedtvjdghosdvnht78gedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rt340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78gedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rtgedtvjdghosdvnht78340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rt340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rt8340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rt340a57qw3f075fnbeiyrtfsneryeo07t6sgy9e4m0t67hnsvy9rt"}
res1 = 11
mes2 = {"conversation_id" : 999, "sender_id" : 1, "content" : "Hello!"}
res2 = None
mes3 = {"conversation_id" : 1, "sender_id" : 800, "content" : "Hello!"}
res3 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the messages related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        #This method load the initial values from friendsNet_data_db.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()
        
    def test_case1(self):
        print "#1. CREATE message with very long content"
        resp = self.connection.create_message(mes1)
        result = self.assertEqual(resp, res1)
        
    def test_case2(self):
        print "#2.CREATE message with not existing conversation"
        resp = self.connection.create_message(mes2)
        result = self.assertEqual(resp, res2)
        
    def test_case3(self):
        print "#3.CREATE message with not existing sender"
        resp = self.connection.create_message(mes3)
        result = self.assertEqual(resp, res3)
        
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()     