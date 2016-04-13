import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

conv1 = {"user1_id" : 1, "user2_id" : 2}
res1 = 5
conv2 = {"user1_id" : 100, "user2_id" : 2}
res2 = None
conv3 = {"user1_id" : 4, "user2_id" : 1}
res3 = None
conv4 = {"conversation_id" : 1}
res4 = [{"message_id" : 2, "conversation_id" : 1, "sender_id" : 4, "content" : "Hi :) !", "time_sent" : 950}, {"message_id" : 1, "conversation_id" : 1, "sender_id" : 1, "content" : "Hello :)", "time_sent" : 913}]
conv5 = {"conversation_id" : 90}
res5 = None
conv6 = {"conversation_id" : 1, "time_last_message" : 3000}
res6 = True
conv7 = {"conversation_id" : 1}
res7 = True
conv8 = {"conversation_id" : 90}
res8 = False
conv9 = {"user_id" : 1}
res9 = [{"conversation_id" : 4, "user1_id" : 3, "user2_id" : 1, "time_last_message" : 1427}, {"conversation_id" : 1, "user1_id" : 1, "user2_id" : 4, "time_last_message" : 950}]
conv10 = {"user_id" : 5}
res10 = None
conv11 = {"user_id" : 100}
res11 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the conversations related methods.
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
        print "#1. CREATE conversation between two users who have never messaged before"
        resp = self.connection.create_conversation(conv1)
        result = self.assertEqual(resp, res1)
    def test_case2(self):
        print "#2. CREATE conversation with one not existing user"
        resp = self.connection.create_conversation(conv2)
        result = self.assertEqual(resp, res2)        
    def test_case3(self):
        print "#3. CREATE conversation between two users who have already messaged before"
        resp = self.connection.create_conversation(conv3)
        result = self.assertEqual(resp, res3)        
    def test_case4(self):
        print "#4. GET messages from existing conversation"
        resp = self.connection.get_messages_for_conversation(conv4["conversation_id"])
        result = self.assertEqual(resp, res4)        
    def test_case5(self):
        print "#5. GET messages from not existing conversation"
        resp = self.connection.get_messages_for_conversation(conv5["conversation_id"])
        result = self.assertEqual(resp, res5)                
    def test_case6(self):
        print "#6. UPDATE conversation (only time of last modify)"
        resp = self.connection.update_conversation(conv6["conversation_id"], conv6["time_last_message"])
        result = self.assertEqual(resp, res6)
    def test_case7(self):
        print "#7. DELETE existing conversation"
        resp = self.connection.delete_conversation(conv7["conversation_id"])
        result = self.assertEqual(resp, res7)
    def test_case8(self):
        print "#8. DELETE not existing conversation"
        resp = self.connection.delete_conversation(conv8["conversation_id"])
        result = self.assertEqual(resp, res8)
    def test_case9(self):
        print "#9. READ conversations of user who is in at least one conversation"
        resp = self.connection.get_conversations_for_user(conv9["user_id"])
        result = self.assertEqual(resp, res9)
    def test_case10(self):
        print "#10. READ conversations of user who isn't in any conversation"
        resp = self.connection.get_conversations_for_user(conv10["user_id"])
        result = self.assertEqual(resp, res10)
    def test_case11(self):
        print "#11. READ conversations of user who with not existing id"
        resp = self.connection.get_conversations_for_user(conv11["user_id"])
        result = self.assertEqual(resp, res11)                
            
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()