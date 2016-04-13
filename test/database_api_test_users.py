import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

user1 = {"email" : "anto95umast@live.it", "password" : "cbadasjdhaskdjhaskdha", "first_name" : "Antonio", "middle_name" : "Francesco", "surname" : "Antonino", "age" : 20, "gender" : 0}
res1 = 8
user2 = {"email" : "email1@gmail.com", "password" : "cbadasjdhaskdjhaskdha", "first_name" : "Antonio", "middle_name" : "Francesco", "surname" : "Antonino", "age" : 20, "gender" : 0}
res2 = None
user3 = {"email" : "anto95umast@live.it", "password" : "a", "first_name" : "Antonio", "middle_name" : "Francesco", "surname" : "Antonino", "age" : 20, "gender" : 0}
res3 = None
user4 = {"email" : "anto95umast2@live.it", "password" : "cbadasjdhaskdjhaskdha", "first_name" : "Antonio", "middle_name" : "Francesco", "surname" : "Antonino", "age" : 20, "gender" : 4}
res4 = None
user5 = {"email" : "email1@gmail.com", "password" : "12345678"}
res5 = 1
user6 = {"email" : "anto94umast@live.it", "password" : "cbadasjdhaskdjhaskdha"}
res6 = None
user7 = {"email" : "anto95umast@live.it", "password" : "i_dont_exist"}
res7 = None
user8 = {"user_id" : 1}
res8 = {"user_id" : 1, "first_name" : "Antonio", "middle_name" : None, "surname" : "Antonino", "prof_picture_id" : None, "age" : 20, "gender" : 0}
user9 = {"user_id" : 90}
res9 = None
user10 = {"user_id" : 90}
res10 = False
user11 = {"user_id" : 3, "values" : {"password" : "correctNewPassword!"}}
res11 = True
user12 = {"user_id" : 3, "values" : {"password" : "incrrct"}}
res12 = False
user13 = {"user_id" : 3, "values" : {"prof_picture_id" : 2, "gender" : 10}}
res13 = False
user14 = {"user_id" : 3, "values" : {"prof_picture_id" : 1000, "gender" : 1}}
res14 = False
user15 = {"user_id" : 3, "values" : {"prof_picture_id" : 1}}
res15 = True
user16 = {"user_id" : 1}
res16 = True
user17 = {"user_id" : 1000}
res17 = False
user18 = {"user_id" : 2}
res18 =  [{"status_id" : 2, "creator_id" : 1, "content" : "Good afternoon!", "creation_time" : 80},
          {"status_id" : 1, "creator_id" : 1, "content" : "Good morning!", "creation_time" : 50}]
user19 =  {"user_id" : 5}
res19 = None
user20 = {"user_id" : 7}
res20 = None
user21 = {"user_id" : 200} 
res21 = None
user22 = {"first_name" : "Anton", "surname" : "Antonin"}
res22 = [{"user_id" : 1, "first_name" : "Antonio", "middle_name" : None, "surname" : "Antonino", "prof_picture_id" : None, "age" : 20, "gender" : 0}]
user23 = {"first_name" : "Filippo", "surname" : "Poncio"}
res23 = None
user24 = {"user_id" : 1}
res24 = [{"group_id" : 1, "user_id" : 1, "administrator" : 1}]
user25 = {"user_id" : 6}
res25 = None
user26 = {"user_id" : 99}
res26 = None
	  
class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the users related methods.
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
    	print "#1.CREATE user with unique email and correct password"
    	resp = self.connection.create_user(user1)
    	result = self.assertEqual(resp,res1)

    def test_case2(self):
    	print "#2.CREATE user with double email"
    	resp = self.connection.create_user(user2)
    	result = self.assertEqual(resp, res2)

    def test_case3(self):
    	print "#3.CREATE user with short password"
    	resp = self.connection.create_user(user3)
    	result = self.assertEqual(resp, res3)

    def test_case4(self):
    	print "#4.CREATE user with gender out of range"
    	resp = self.connection.create_user(user4)
    	result = self.assertEqual(resp, res4)


    def test_case5(self):
    	print "#5.READ user with email and password existing"
    	resp = self.connection.get_user_id(user5["email"], user5["password"])
	result = self.assertEqual(resp, res5)

    def test_case6(self):
    	print "#6.READ user with email not existing"
    	resp = self.connection.get_user_id(user6["email"], user6["password"])
    	result = self.assertEqual(resp, res6)

    def test_case7(self):
    	print "#7.READ user with password not existing"
    	resp = self.connection.get_user_id(user7["email"], user7["password"])
    	result = self.assertEqual(resp, res7)

    def test_case8(self):
    	print "#8.READ user with existing id"
    	resp = self.connection.get_user_information(user8["user_id"])
    	result = self.assertEqual(resp, res8)

    def test_case9(self):
    	print "#9.READ user with not existing id"
    	resp = self.connection.get_user_information(user9["user_id"])
    	result = self.assertEqual(resp, res9)

    def test_case10(self):
    	print "#10.UPDATE user with not existing id"
    	resp = self.connection.update_user(user10["user_id"], {})
    	result = self.assertEqual(resp, res10)

    def test_case11(self):
    	print "#11.UPDATE user with new password correct"
    	resp = self.connection.update_user(user11["user_id"], user11["values"])
    	result = self.assertEqual(resp, res11)

    def test_case12(self):
    	print "#12.UPDATE user with new password incorrect"
    	resp = self.connection.update_user(user12["user_id"], user12["values"])
    	result = self.assertEqual(resp, res12)

    def test_case13(self):
    	print "#13.UPDATE user with new prof_pic_correct and gender out of range"
    	resp = self.connection.update_user(user13["user_id"], user13["values"])
    	result = self.assertEqual(resp, res13)

    def test_case14(self):
    	print "#14.UPDATE user with new prof_pic incorrect and correct range"
    	resp = self.connection.update_user(user14["user_id"], user14["values"])
    	result = self.assertEqual(resp, res14)

    def test_case15(self):
    	print "#15.UPDATE user with prof_pic correct"
    	resp = self.connection.update_user(user15["user_id"], user15["values"])
    	result = self.assertEqual(resp, res15)

    def test_case16(self):
    	print "#16.DELETE user with existing id"
    	resp = self.connection.delete_user(user16["user_id"])
    	result = self.assertEqual(resp, res16)

    def test_case17(self):
    	print "#17.DELETE user with not existing id"
    	resp = self.connection.delete_user(user17["user_id"])
    	result = self.assertEqual(resp, res17)
	
    def test_case18(self):
        print "#18.GET friends' statuses for user with friends who have totally published at least one status"
        resp = self.connection.get_friends_statuses_for_user(user18["user_id"])
        result = self.assertEqual(resp, res18)
	
    def test_case19(self):
        print "#19.GET friends' statuses for user with friends who totally haven't published any status"
        resp = self.connection.get_friends_statuses_for_user(user19["user_id"])
        result = self.assertEqual(resp, res19)    
	
    def test_case20(self):
        print "#20.GET friends' statuses for user with no friend"
        resp = self.connection.get_friends_statuses_for_user(user20["user_id"])
        result = self.assertEqual(resp, res20)
	
    def test_case21(self):
        print "#21.GET friends' statuses for not existing user"
        resp = self.connection.get_friends_statuses_for_user(user21["user_id"])
        result = self.assertEqual(resp, res21)
	
    def test_case22(self):
        print "#22.GET users with long match in parameters"
        resp = self.connection.search_user(user22["first_name"], user22["surname"])
        result = self.assertEqual(resp, res22)
	
    def test_case23(self):
        print "#23.GET users with no match in parameters"
        resp = self.connection.search_user(user23["first_name"], user23["surname"])
        result = self.assertEqual(resp, res23)

    def test_case24(self):
        print "#24.GET groups for user in at least one group"
        resp = self.connection.get_groups_for_user(user24["user_id"])
        result = self.assertEqual(resp, res24)

    def test_case25(self):
        print "#25.GET groups for user in no group"
        resp = self.connection.get_groups_for_user(user25["user_id"])
        result = self.assertEqual(resp, res25)

    def test_case26(self):
        print "#26.GET groups for user who doesn't exist"
        resp = self.connection.get_groups_for_user(user26["user_id"])
        result = self.assertEqual(resp, res26)

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()