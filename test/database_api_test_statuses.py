import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

stat1 = {"creator_id" : 1, "content" : "Hellooooo"}
res1 = 10
stat2 = {"creator_id" : 100, "content" : "tryy"}
res2 = None
stat3 = {"user_id" : 2}
res3 = [{"status_id" : 3, "creator_id" : 2, "content" : "I'm here!!!!", "creation_time" : 90}]
stat4 = {"user_id" : 90}
res4 = None
stat5 = {"group_id" : 2}
res5 = [{"status_id" : 9, "creator_id" : 3, "content" : "Hello everyone :)", "creation_time" : 1931}]
stat6 = {"group_id" : 1}
res6 = None
stat7 = {"group_id" : 90}
res7 = None
stat8 = {"status_id" : 1, "description" : "New description"}
res8 = True
stat9 = {"status_id" : 299, "description" : "New description"}
res9 = False
stat10 = {"status_id" : 1}
res10 = [{"media_item_id" : 1, "media_item_type" : 0, "url" : "/friendsNet/media_uploads/media1.jpg", "description" : "Flowers are wonderful!"}]
stat11 = {"status_id" : 10}
res11 = None
stat12 = {"status_id" : 200}
res12 = None
stat13 = {"status_id" : 1, "media_id" : 9}
res13 = True
stat14 = {"status_id" : 1, "media_id" : 1}
res14 = False
stat15 = {"status_id" : 1, "media_id" : 900}
res15 = False
stat16 = {"status_id" : 100, "media_id" : 2}
res16 = False
stat17 = {"status_id" : 1, "media_id" : 1}
res17 = True
stat18 = {"status_id" : 1, "media_id" : 2}
res18 = False
stat19 = {"status_id" : 100, "media_id" : 1}
res19 = False
stat20 = {"status_id" : 1}
res20 = True
stat21 = {"status_id" : 200}
res21 = False
stat22 = {"status" : {"creator_id" : 1, "content" : "Hi :)"}, "group_id" : 3}
res22 = 10
stat23 = {"status" : {"creator_id" : 1, "content" : "Hi :)"}, "group_id" : 99}
res23 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the statuses related methods.
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
        print "#1.CREATE status with correct user id"
        resp = self.connection.create_status(stat1)
        result = self.assertEqual(resp, res1)
        
    def test_case2(self):
        print "#2. CREATE status with not existing user id"
        resp = self.connection.create_status(stat2)
        result = self.assertEqual(resp, res2)        
        
    def test_case3(self):
        print "#3. READ statuses for user who posted at least one status"
        resp = self.connection.get_statuses_for_user(stat3["user_id"])
        result = self.assertEqual(resp, res3)        
        
    def test_case4(self):
        print "#4. READ status of not existing user id"
        resp = self.connection.get_statuses_for_user(stat4["user_id"])
        result = self.assertEqual(resp, res4)        
        
    def test_case5(self):
        print "#5. READ statuses from group which has at least one status published"
        resp = self.connection.get_statuses_for_group(stat5["group_id"])
        result = self.assertEqual(resp, res5)        
        
    def test_case6(self):
        print "#6. READ statuses from group which hasn't any status published"
        resp = self.connection.get_statuses_for_group(stat6["group_id"])
        result = self.assertEqual(resp, res6)        
        
    def test_case7(self):
        print "#7. READ statuses from group with not existing id"
        resp = self.connection.get_statuses_for_group(stat7["group_id"])
        result = self.assertEqual(resp, res7)        
    
    def test_case8(self):
        print "#8. UPDATE status description with existing id"
        resp = self.connection.update_status_content(stat8["status_id"], stat8["description"])
        result = self.assertEqual(resp, res8)
        
    def test_case9(self):
        print "#9. UPDATE status description with not existing id"
        resp = self.connection.update_status_content(stat9["status_id"], stat9["description"])
        result = self.assertEqual(resp, res9)        
        
    def test_case10(self):
        print "#10. READ media attached to a status with at least one media attached"
        resp = self.connection.get_media_for_status(stat10["status_id"])
        result = self.assertEqual(resp, res10)
        
    def test_case11(self):
        print "#11. READ media attached to a status with no media attached"
        resp = self.connection.get_media_for_status(stat11["status_id"])
        result = self.assertEqual(resp, res11)        
        
    def test_case12(self):
        print "#12. READ media attached to a status with not existing id"
        resp = self.connection.get_media_for_status(stat12["status_id"])
        result = self.assertEqual(resp, res12)        
        
    def test_case13(self):
        print "#13. ADD media to status"
        resp = self.connection.add_media_to_status(stat13["status_id"], stat13["media_id"])
        result = self.assertEqual(resp, res13)
    
    def test_case14(self):
        print "#14. ADD media to status which already contain that media"
        resp = self.connection.add_media_to_status(stat14["status_id"], stat14["media_id"])
        result = self.assertEqual(resp, res14)        
        
    def test_case15(self):
        print "#15. ADD not existing media to status"
        resp = self.connection.add_media_to_status(stat15["status_id"], stat15["media_id"])
        result = self.assertEqual(resp, res15)        
        
    def test_case16(self):
        print "#16. ADD media to not existing status"
        resp = self.connection.add_media_to_status(stat16["status_id"], stat16["media_id"])
        result = self.assertEqual(resp, res16)        
        
    def test_case17(self):
        print "#17. DELETE media from status"
        resp = self.connection.delete_media_from_status(stat17["status_id"], stat17["media_id"])
        result = self.assertEqual(resp, res17)
        
    def test_case18(self):
        print "#18. DELETE media not attached from status"
        resp = self.connection.delete_media_from_status(stat18["status_id"], stat18["media_id"])
        result = self.assertEqual(resp, res18)        
            
    def test_case19(self):
        print "#19. DELETE media from not existing status"
        resp = self.connection.delete_media_from_status(stat19["status_id"], stat19["media_id"])
        result = self.assertEqual(resp, res19)        

    def test_case20(self):
        print "#20. DELETE status"
        resp = self.connection.delete_status(stat20["status_id"])
        result = self.assertEqual(resp, res20)
        
    def test_case21(self):
        print "#21. DELETE status with not existing id"
        resp = self.connection.delete_status(stat21["status_id"])
        result = self.assertEqual(resp, res21)

    def test_case22(self):
        print "#22. CREATE status for existing group"
        resp = self.connection.create_status(stat22["status"], stat22["group_id"])
        result = self.assertEqual(resp, res22)

    def test_case23(self):
        print "#23. CREATE status for group which doesn't exist"
        resp = self.connection.create_status(stat23["status"], stat23["group_id"])
        result = self.assertEqual(resp, res23)

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()        