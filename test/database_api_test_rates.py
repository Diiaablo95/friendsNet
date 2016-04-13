import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

rate1 = {"status_id" : 3, "values" : {"user_id" : 4, "rate" : 5}}
res1 = 16
rate2 = {"status_id" : 2, "values" : {"user_id" : 3, "rate" : 5}}
res2 = 16
rate3 = {"status_id" : 200, "values" : {"user_id" : 2, "rate" : 2}}
res3 = None
rate4 = {"status_id" : 1, "values" : {"user_id" : 100, "rate" : 4}}
res4 = None
rate5 = {"status_id" : 1, "values" : {"user_id" : 2, "rate" : 3}}
res5 = None
rate6 = {"status_id" : 1, "values" : {"user_id" : 1, "rate" : 9}}
res6 = None
rate7 = {"status_id" : 1}
res7 = [{"rate_id" : 1, "status_id" : 1, "user_id" : 2, "rate" : 4}]
rate8 = {"status_id" : 3}
res8 = None
rate9 = {"status_id" : 1000}
res9 = None
rate10 = {"rate_id" : 1, "rate" : 3}
res10 = True
rate11 = {"rate_id" : 1, "rate" : 4}
res11 = False
rate12 = {"rate_id" : 1, "rate" : 90}
res12 = False
rate13 = {"rate_id" : 200, "rate" : 2}
res13 = False
rate14 = {"rate_id" : 1}
res14 = True
rate15 = {"rate_id" : 900}
res15 = False
rate16 = {"user_id" : 1}
res16 = [{"rate_id" : 2, "status_id" : 2, "user_id" : 1, "rate" : 4},
         {"rate_id" : 7, "status_id" : 5, "user_id" : 1, "rate" : 4},
         {"rate_id" : 14, "status_id" : 8, "user_id" : 1, "rate" : 4}]
rate17 = {"user_id" : 5}
res17 = None
rate18 = {"user_id" : 100}
res18 = None

class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the rates related methods.
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
        print "#1.CREATE rate for existing status with no previous rate"
        resp = self.connection.add_rate_to_status(rate1["status_id"], rate1["values"])
        result = self.assertEqual(resp, res1)

    def test_case2(self):
        print "#2.CREATE rate for existing  status with previous rates"
        resp = self.connection.add_rate_to_status(rate2["status_id"], rate2["values"])
        result = self.assertEqual(resp, res2)

    def test_case3(self):
        print "#3.CREATE rate for not existing status"
        resp = self.connection.add_rate_to_status(rate3["status_id"], rate3["values"])
        result = self.assertEqual(resp, res3)

    def test_case4(self):
        print "#4.CREATE rate from not existing user"
        resp = self.connection.add_rate_to_status(rate4["status_id"], rate4["values"])
        result = self.assertEqual(resp, res4)
        
    def test_case5(self):
        print "#5.CREATE rate with not unique (status_id, user_id)"
        resp = self.connection.add_rate_to_status(rate5["status_id"], rate5["values"])
        result = self.assertEqual(resp, res5)
        
    def test_case6(self):
        print "#6.CREATE rate with rate out of range"
        resp = self.connection.add_rate_to_status(rate6["status_id"], rate6["values"])
        result = self.assertEqual(resp, res6)
        
    def test_case7(self):
        print "#7.READ rates for status with rates"            
        resp = self.connection.get_rates_for_status(rate7["status_id"])
        result = self.assertEqual(resp, res7)

    def test_case8(self):
        print "#8.READ rates for status with no rates"
        resp = self.connection.get_rates_for_status(rate8["status_id"])
        result = self.assertEqual(resp, res8)

    def test_case9(self):
        print "#9.READ rates for not existing status"            
        resp = self.connection.get_rates_for_status(rate9["status_id"])
        result = self.assertEqual(resp, res9)

    def test_case10(self):
        print "#10.UPDATE rate with different content"
        resp = self.connection.update_rate_value(rate10["rate_id"], rate10["rate"])
        result = self.assertEqual(resp, res10)

    def test_case11(self):
        print "#11.UPDATE rate with the same content"            
        resp = self.connection.update_rate_value(rate11["rate_id"], rate11["rate"])
        result = self.assertEqual(resp, res11)
        
    def test_case12(self):
        print "#12. UPDATE rate with value out of range"
        resp = self.connection.update_rate_value(rate12["rate_id"], rate12["rate"])
        result = self.assertEqual(resp, res12)

    def test_case13(self):
        print "#13.UPDATE not existing rate"            
        resp = self.connection.update_rate_value(rate13["rate_id"], rate13["rate"])
        result = self.assertEqual(resp, res13)

    def test_case14(self):
        print "#14.DELETE existing rate"  
        resp = self.connection.delete_rate(rate14["rate_id"])
        result = self.assertEqual(resp, res14)

    def test_case15(self):
        print "#15.DELETE not existing rate"            
        resp = self.connection.delete_rate(rate15["rate_id"])
        result = self.assertEqual(resp, res15)

    def test_case16(self):
        print "#16.READ rates for user who rated at least once"            
        resp = self.connection.get_rates_for_user(rate16["user_id"])
        result = self.assertEqual(resp, res16)

    def test_case17(self):
        print "#17.READ rates for user who has never rated"
        resp = self.connection.get_rates_for_user(rate17["user_id"])
        result = self.assertEqual(resp, res17)

    def test_case18(self):
        print "#18.READ rates for not existing user"
        resp = self.connection.get_rates_for_user(rate18["user_id"])
        result = self.assertEqual(resp, res18)
        
if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()        