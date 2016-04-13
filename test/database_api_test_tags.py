import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

tag1 = {"status_id" : 1, "user_id" : 3}
res1 = True
tag2 = {"status_id" : 90, "user_id" : 1}
res2 = False
tag3 = {"status_id" : 1, "user_id" : 90}
res3 = False
tag4 = {"status_id" : 1, "user_id" : 2}
res4 = False
tag5 = {"status_id" : 3}
res5 = [{"user_id" : 3, "first_name" : "Mikko", "middle_name" : None, "surname" : "Yliniemi", "prof_picture_id" : None, "age" : 28, "gender" : 0}]
tag6 = {"status_id" : 7}
res6 = None
tag7 = {"status_id" : 19}
res7 = None
tag8 = {"status_id" : 1, "user_id" : 2}
res8 = True
tag9 = {"status_id" : 1, "user_id" : 3}
res9 = False
tag10 = {"status_id" : 900, "user_id" : 1}
res10 = False
tag11 = {"user_id" : 1}
res11 = [{"status_id" : 4, "creator_id" : 3, "content" : "So sleepy....",  "creation_time" : 100},
         {"status_id" : 2, "creator_id" : 1, "content" : "Good afternoon!", "creation_time" : 80}]
tag12 = {"user_id" : 5}
res12 = None
tag13 = {"user_id" : 100}
res13 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the tags related methods.
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
        print "#1.CREATE tag for existing status and existing user id not tagged"
        resp = self.connection.add_tag_to_status(tag1["status_id"], tag1["user_id"])
        result = self.assertEqual(resp,res1)
        
    def test_case2(self):
        print "#2.CREATE tag for not existing status"
        resp = self.connection.add_tag_to_status(tag2["status_id"], tag2["user_id"])
        result = self.assertEqual(resp,res2)
        
    def test_case3(self):
        print "#3.CREATE tag for not existing user id"
        resp = self.connection.add_tag_to_status(tag3["status_id"], tag3["user_id"])
        result = self.assertEqual(resp,res3)
        
    def test_case4(self):
        print "#4. CREATE tag for already existing (group_id-user_id) couple"
        resp = self.connection.add_tag_to_status(tag4["status_id"], tag4["user_id"])
        result = self.assertEqual(resp,res4)

    def test_case5(self):
        print "#5.READ tags for existing status with at least one tag"
        resp = self.connection.get_tagged_users_for_status(tag5["status_id"])
        result = self.assertEqual(resp,res5)
        
    def test_case6(self):
        print "#6.READ tags for existing status with no tags"
        resp = self.connection.get_tagged_users_for_status(tag6["status_id"])
        result = self.assertEqual(resp,res6)
        
    def test_case7(self):
        print "#7.READ tags for not existing status"
        resp = self.connection.get_tagged_users_for_status(tag7["status_id"])
        result = self.assertEqual(resp,res7)

    def test_case8(self):
        print "#8.DELETE existing tag for existing status"
        resp = self.connection.delete_tag(tag8["status_id"], tag8["user_id"])
        result = self.assertEqual(resp,res8)
        
    def test_case9(self):
        print "#9.DELETE not existing tag for existing status"
        resp = self.connection.delete_tag(tag9["status_id"], tag9["user_id"])
        result = self.assertEqual(resp,res9)
        
    def test_case10(self):
        print "#10.DELETE tag for not existing status"
        resp = self.connection.delete_tag(tag10["status_id"], tag10["user_id"])
        result = self.assertEqual(resp,res10)
        
    def test_case11(self):
        print "#11.READ tags for user with at least one tag"
        resp = self.connection.get_tagged_statuses_for_user(tag11["user_id"])
        result = self.assertEqual(resp,res11)
        
    def test_case12(self):
        print "#12.READ tags for user with no tags"
        resp = self.connection.get_tagged_statuses_for_user(tag12["user_id"])
        result = self.assertEqual(resp,res12)
        
    def test_case13(self):
        print "#13.READ tags for not existing user"
        resp = self.connection.get_tagged_statuses_for_user(tag13["user_id"])
        result = self.assertEqual(resp,res13)

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()