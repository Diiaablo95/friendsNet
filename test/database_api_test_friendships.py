import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

fri1 = {"user1_id" : 2, "user2_id" : 4}
res1 = 7
fri2 = {"user1_id" : 3, "user2_id" : 1}
res2 = None
fri3 = {"user1_id" : 1, "user2_id" : 10}
res3 = None
fri4 = {"user1_id" : 2}
res4 = [{"friendship_id" : 1, "user1_id" : 1, "user2_id" : 2, "friendship_status" : 1, "friendship_start" : 100},
        {"friendship_id" : 3, "user1_id" : 3, "user2_id" : 2, "friendship_status" : 0, "friendship_start" : None}]
fri5 = {"user1_id" : 7}
res5 = None
fri6 = {"user1_id" : 1000}
res6 = None
fri7 = {"friendship_id" : 3}
res7 = True
fri8 = {"friendship_id" : 1}
res8 = True
fri9 = {"friendship_id" : 3}
res9 = True
fri10 = {"friendship_id" : 30}
res10 = False


class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the friendships related methods.
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
        print "#1. CREATE friendship between two not friends-users"
        resp = self.connection.create_friendship(fri1["user1_id"], fri1["user2_id"])
        result = self.assertEqual(resp, res1)
    def test_case2(self):
        print "#2. CREATE friendship between two users already friends"    
        resp = self.connection.create_friendship(fri2["user1_id"], fri2["user2_id"])
        result = self.assertEqual(resp, res2)
    def test_case3(self):
        print "#3. CREATE friendship with an incorrect user_id"
        resp = self.connection.create_friendship(fri3["user1_id"], fri3["user2_id"])
        result = self.assertEqual(resp, res3)
    def test_case4(self):
        print "#4. READ friendships of a user with friends"
        resp = self.connection.get_friendships_for_user(fri4["user1_id"])
        result = self.assertEqual(resp, res4)
    def test_case5(self):
        print "#5. READ friendships of a user without friends"
        resp = self.connection.get_friendships_for_user(fri5["user1_id"])
        result = self.assertEqual(resp, res5)
    def test_case6(self):
        print "#6. READ friendships of a user with incorrect id"
        resp = self.connection.get_friendships_for_user(fri6["user1_id"])
        result = self.assertEqual(resp, res6)
    def test_case7(self):
        print "#7. ACCEPT friendship between two not friends-users"
        resp = self.connection.accept_friendship(fri7["friendship_id"])
        result = self.assertEqual(resp, res7)
    def test_case8(self):
        print "#8. ACCEPT friendship between two users already friends"
        resp = self.connection.accept_friendship(fri8["friendship_id"])
        result = self.assertEqual(resp, res8)
    def test_case9(self):
        print "#9. DELETE friendship with existing id"
        resp = self.connection.delete_friendship(fri9["friendship_id"])
        result = self.assertEqual(resp, res9)
    def test_case10(self):
        print "#10. DELETE friendship with not existing id"            
        resp = self.connection.delete_friendship(fri10["friendship_id"])
        result = self.assertEqual(resp, res10)
            
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()