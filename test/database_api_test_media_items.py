import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)


media1 = {"media_type" : 0, "url" : "http://url30.com", "description" : "Descriptionnn"}
res1 = 11
media2 = {"media_type" : 5, "url" : "http://url1212.com"}
res2 = None
media3 = {"media_type" : 1, "url" : "http://url124.com"}
res3 = 11
media4 = {"media_type" : 1, "url" : "/friendsNet/media_uploads/media1.jpg", "description" : None}
res4 = None
media5 = {"media_id" : 1, "description" : None}
res5 = True
media6 = {"media_id" : 1, "description" : "new description!"}
res6 = True
media7 = {"media_id" : 10000, "description" : None}
res7 = False
media8 = {"media_id" : 1}
res8 = True
media9 = {"media_id" : 1000}
res9 = False
res10 = 10

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the media items related methods.
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
        print "#1.CREATE media with correct type and description"
        resp = self.connection.create_media(media1)
        result = self.assertEqual(resp, res1)
        
    def test_case2(self):
        print "#2.CREATE media with wrong type"
        resp = self.connection.create_media(media2)
        result = self.assertEqual(resp, res2)    
        
    def test_case3(self):
        print "#3.CREATE media with correct type and no description"
        resp = self.connection.create_media(media3)
        result = self.assertEqual(resp, res3)            
        
    def test_case4(self):
        print "#4.CREATE media with existing url"
        resp = self.connection.create_media(media4)
        result = self.assertEqual(resp, res4)                
        
    def test_case5(self):
        print "#5.UPDATE: remove description from media with existing id"
        resp = self.connection.update_media_description(media5["media_id"], media5["description"])
        result = self.assertEqual(resp, res5)                
        
    def test_case6(self):
        print "#6.UPDATE: modifying description to media with existing id"
        resp = self.connection.update_media_description(media6["media_id"], media6["description"])
        result = self.assertEqual(resp, res6)    
        
    def test_case7(self):
        print "#7.UPDATE: updating media with not existing id"
        resp = self.connection.update_media_description(media7["media_id"], media7["description"])
        result = self.assertEqual(resp, res7)    
        
    def test_case8(self):
        print "#8.DELETE media with existing id"
        resp = self.connection.delete_media_item(media8["media_id"])
        result = self.assertEqual(resp, res8)    
        
    def test_case9(self):
        print "#9.DELETE media with not existing id"
        resp = self.connection.delete_media_item(media9["media_id"])
        result = self.assertEqual(resp, res9)

    def test_case10(self):
        print "#10.GET last media item id"
        resp = self.connection.get_last_media_item_id()
        result = self.assertEqual(resp, res10)
        
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()