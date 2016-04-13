import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

com1 = {"status_id" : 2, "values" : {"user_id" : 4, "content" : "Trying to be the first!"}}
res1 = 12
com2 = {"status_id" : 1, "values" : {"user_id" : 2, "content" : "Ehi!"}}
res2 = 12
com3 = {"status_id" : 200, "values" : {"user_id" : 2, "content" : "Ehi!"}}
res3 = None
com4 = {"status_id" : 1, "values" : {"user_id" : 100, "content" : "Ehi!"}}
res4 = None
com5 = {"status_id" : 4}
res5 = [{"comment_id" : 6, "status_id" : 4, "user_id" : 1, "content" : "Hello :D !", "creation_time" : 120}]
com6 = {"status_id" : 2}
res6 = None
com7 = {"status_id" : 1000}
res7 = None
com8 = {"comment_id" : 1, "content" : "No."}
res8 = True
com9 = {"comment_id" : 1, "content" : "Ahahahaah"}
res9 = True
com10 = {"comment_id" : 200, "content" : "Ahahahaah"}
res10 = False
com11 = {"comment_id" : 1}
res11 = True
com12 = {"comment_id" : 900}
res12 = False
com13 = {"user_id" : 3}
res13 = [{"comment_id" : 9, "status_id" : 5, "user_id" : 3, "content" : "Nothing ahah", "creation_time" : 170},
         {"comment_id" : 7, "status_id" : 5, "user_id" : 3, "content" : "Ehi :)))", "creation_time" : 155}]
com14 = {"user_id" : 5}
res14 = None
com15 = {"user_id" : 100}
res15 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the comments related methods.
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
        print "#1.CREATE comment for existing status with no previous comment"
        resp = self.connection.add_comment_to_status(com1["status_id"], com1["values"])
        result = self.assertEqual(resp, res1)
        
    def test_case2(self):
        print "#2.CREATE comment for existing  status with previous comments"
        resp = self.connection.add_comment_to_status(com2["status_id"], com2["values"])
        result = self.assertEqual(resp, res2)
        
    def test_case3(self):
        print "#3.CREATE comment for not existing status"
        resp = self.connection.add_comment_to_status(com3["status_id"], com3["values"])
        result = self.assertEqual(resp, res3)
        
    def test_case4(self):
        print "#4.CREATE comment from not existing user"
        resp = self.connection.add_comment_to_status(com4["status_id"], com4["values"])
        result = self.assertEqual(resp, res4)
        
    def test_case5(self):
        print "#5.READ comments for status with comments"            
        resp = self.connection.get_comments_for_status(com5["status_id"])
        result = self.assertEqual(resp, res5)
        
    def test_case6(self):
        print "#6.READ comment for status with no comments"
        resp = self.connection.get_comments_for_status(com6["status_id"])
        result = self.assertEqual(resp, res6)
        
    def test_case7(self):
        print "#7.READ comment for not existing status"            
        resp = self.connection.get_comments_for_status(com7["status_id"])
        result = self.assertEqual(resp, res7)
        
    def test_case8(self):
        print "#8.UPDATE comment with different content"
        resp = self.connection.update_comment_content(com8["comment_id"], com8["content"])
        result = self.assertEqual(resp, res8)
        
    def test_case9(self):
        print "#9.UPDATE comment with the same content"            
        resp = self.connection.update_comment_content(com9["comment_id"], com9["content"])
        result = self.assertEqual(resp, res9)
        
    def test_case10(self):
        print "#10.UPDATE not existing comment"            
        resp = self.connection.update_comment_content(com10["comment_id"], com10["content"])
        result = self.assertEqual(resp, res10)
        
    def test_case11(self):
        print "#11.DELETE existing comment"  
        resp = self.connection.delete_comment(com11["comment_id"])
        result = self.assertEqual(resp, res11)
        
    def test_case12(self):
        print "#12.DELETE not existing comment"            
        resp = self.connection.delete_comment(com12["comment_id"])
        result = self.assertEqual(resp, res12)
        
    def test_case13(self):
        print "#13.READ comments for user who commented at least once"            
        resp = self.connection.get_comments_for_user(com13["user_id"])
        result = self.assertEqual(resp, res13)
        
    def test_case14(self):
        print "#14.READ comments for user who has never commented"
        resp = self.connection.get_comments_for_user(com14["user_id"])
        result = self.assertEqual(resp, res14)
        
    def test_case15(self):
        print "#15.READ comments for not existing user"
        resp = self.connection.get_comments_for_user(com15["user_id"])
        result = self.assertEqual(resp, res15)
            
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()        