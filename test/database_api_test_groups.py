import unittest
from friendsNet import database

DB_PATH = "db/dump_database_test.db"
ENGINE = database.Engine(DB_PATH)

group1 = {"name" : "Group4", "privacy_level" : 1, "description" : "Group description"}
res1 = 4
group2 = {"name" : "Group4", "prof_picture_id" : 20000, "privacy_level" : 2}
res2 = None
group3 = {"name" : "Group4", "privacy_level" : 20}
res3 = None
group4 = {"name" : "Group4", "privacy_level" : 2}
res4 = 4
group5 = 3
res5 = None
group6 = 2
res6 = [{"group_id" : 2, "user_id" : 3, "administrator" : 1}]
group7 = 19
res7 = None
group8 = 1
res8 = None
group9 = 2
res9 = [{"group_id" : 2, "user_id" : 1}, {"group_id" : 2, "user_id" : 4}]
group10 = 10
res10 = None
group11 = 1
res11 = {"group_id" : 1, "name" : "Group1", "prof_picture_id" : None, "privacy_level" : 0, "description" : "Absolutely secret group."}
group12 = 12
res12 = None
group13 = {"group_id" : 1, "values" : {"description" : "New private description (only for members)!"}}
res13 = True
group14 = {"group_id" : 1, "values" : {"privacy_level" : 10}}
res14 = False
group15 = {"group_id" : 1, "values" : {"description" : None}}
res15 = True
group16 = 1
res16 = True
group17 = 17
res17 = False
group18 = {"group_id" : 2, "user_id" : 1}
res18 = True
group19 = {"group_id" : 2, "user_id" : 3}
res19 = False
group20 = {"group_id" : 2, "user_id" : 1}
res20 = True
group21 = {"group_id" : 2, "user_id" : 3}
res21 = False
group22 = {"group_id" : 1, "user_id" : 4}
res22 = True
group23 = {"group_id" : 1, "user_id" : 2}
res23 = False
group24 = {"group_id" : 1, "user_id" : 2}
res24 = True
group25 = {"group_id" : 1, "user_id" : 4}
res25 = False
group26 = {"group_id" : 1, "values" : {"user_id" : 3, "administrator" : 1}}
res26 = True
group27 = {"group_id" : 1, "values" : {"user_id" : 1, "administrator" : 1}}
res27 = False
group28 = {"group_id" : 1, "values" : {"user_id" : 1, "administrator" : 0}}
res28 = True
group29 = {"group_id" : 1, "values" : {"user_id" : 3, "administrator" : 0}}
res29 = False
group30 = {"user_id" : 3}
res30 = [{"group_id" : 1, "user_id" : 3, "administrator" : 0}, {"group_id" : 2, "user_id" : 3, "administrator" : 1}]
group31 = {"user_id" : 4}
res31 = None
group32 = {"user_id" : 100}
res32 = None
group33 = {"group_id" : 2}
res33 = [{"status_id" : 9, "creator_id" : 3, "content" : "Hello everyone :)", "creation_time" :  1931}]
group34 = {"group_id" : 3}
res34 = None
group35 = {"group_id" : 99}
res35 = None



class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the groups related methods.
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
        print "#1.CREATE group with right privacy level and description"
        resp = self.connection.create_group(group1)
        result = self.assertEqual(resp,res1) 
        
    def test_case2(self):
        print "#2.CREATE group with prof pic id not existing"
        resp = self.connection.create_group(group2)
        result = self.assertEqual(resp,res3)
            
    def test_case3(self):
        print "#3.CREATE group with privacy level incorrect"
        resp = self.connection.create_group(group3)
        result = self.assertEqual(resp,res3)         
        
    def test_case4(self):
        print "#4.CREATE group with right privacy level and no description"
        resp = self.connection.create_group(group4)
        result = self.assertEqual(resp,res4) 
            
    def test_case5(self):
        print "#5.READ users from existing group without users"
        resp = self.connection.get_members_for_group(group5)
        result = self.assertEqual(resp,res5)
            
    def test_case6(self):
        print "#6.READ users from existing group with users"
        resp = self.connection.get_members_for_group(group6)
        result = self.assertEqual(resp,res6) 
            
    def test_case7(self):
        print "#7.READ users from unexisting group"
        resp = self.connection.get_members_for_group(group7)
        result = self.assertEqual(resp,res7)
            
    def test_case8(self):
        print "#8.READ requests for an existing group with no pending requests"
        resp = self.connection.get_requests_for_group(group8)
        result = self.assertEqual(resp,res8) 
            
    def test_case9(self):
        print "#9.READ requests for an existing group with pending requests"
        resp = self.connection.get_requests_for_group(group9)
        result = self.assertEqual(resp,res9)
            
    def test_case10(self):
        print "#10.READ requests for an not existing group"
        resp = self.connection.get_requests_for_group(group10)
        result = self.assertEqual(resp,res10)     
            
    def test_case11(self):
        print "#11.READ info for existing group"
        resp = self.connection.get_information_for_group(group11)
        result = self.assertEqual(resp,res11)     
                
    def test_case12(self):
        print "#12.READ info for an not existing group"
        resp = self.connection.get_information_for_group(group12)
        result = self.assertEqual(resp,res12)
                
    def test_case13(self):
        print "#13. UPDATE existing group with a new description"
        resp = self.connection.update_group(group13["group_id"], group13["values"])
        result = self.assertEqual(resp, res13)
        
    def test_case14(self):
        print "#14. UPDATE existing group with wrong privacy level"
        resp = self.connection.update_group(group14["group_id"], group14["values"])
        result = self.assertEqual(resp, res14)
        
    def test_case15(self):
        print "#15. UPDATE: remove description for existing group"
        resp = self.connection.update_group(group15["group_id"], group15["values"])
        result = self.assertEqual(resp, res15)

    def test_case16(self):
        print "#16. DELETE existing group"
        resp = self.connection.delete_group(group16)
        result = self.assertEqual(resp, res16)
        
    def test_case17(self):
        print "#17. DELETE not existing group"
        resp = self.connection.delete_group(group17)
        result = self.assertEqual(resp, res17)
        
    def test_case18(self):
        print "#18. DELETE request from requesting user"
        resp = self.connection.delete_group_request(group18["group_id"], group18["user_id"])
        result = self.assertEqual(resp, res18)
        
    def test_case19(self):
        print "#19. DELETE request from not requesting user"
        resp = self.connection.delete_group_request(group19["group_id"], group19["user_id"])
        result = self.assertEqual(resp, res19)
        
    def test_case20(self):
        print "#20. ACCEPT request from requesting user"
        resp = self.connection.accept_group_request(group20["group_id"], group20["user_id"])
        result = self.assertEqual(resp, res20)
        
    def test_case21(self):
        print "#21. ACCEPT request from not requesting user"
        resp = self.connection.accept_group_request(group21["group_id"], group21["user_id"])
        result = self.assertEqual(resp, res21)
        
    def test_case22(self):
        print "#22. ADD user not present in the group"
        resp = self.connection.add_member_to_group(group22["group_id"], group22["user_id"])
        result = self.assertEqual(resp, res22)
        
    def test_case23(self):
        print "#23. ADD user already present in the group"
        resp = self.connection.add_member_to_group(group23["group_id"], group23["user_id"])
        result = self.assertEqual(resp, res23)
        
    def test_case24(self):
        print "#24. REMOVE user present in the group"
        resp = self.connection.delete_member(group24["group_id"], group24["user_id"])
        result = self.assertEqual(resp, res24)
        
    def test_case25(self):
        print "#25. REMOVE user not present in the group"
        resp = self.connection.delete_member(group25["group_id"], group25["user_id"])
        result = self.assertEqual(resp, res25)
    
    def test_case26(self):
        print "#26. Promoting user not administrator"
        resp = self.connection.update_group_member(group26["group_id"], group26["values"])
        result = self.assertEqual(resp, res26)
    
    def test_case27(self):
        print "#27. Promoting user already administrator"
        resp = self.connection.update_group_member(group27["group_id"], group27["values"])
        result = self.assertEqual(resp, res27)
            
    def test_case28(self):
        print "#28. Demoting user administrator"
        resp = self.connection.update_group_member(group28["group_id"], group28["values"])
        result = self.assertEqual(resp, res28)
            
    def test_case29(self):
        print "#29. Demoting user not administrator"
        resp = self.connection.update_group_member(group29["group_id"], group29["values"])
        result = self.assertEqual(resp, res29)
    def test_case30(self):
        print "#30. READ groups for a user who is member of at least one group"
        resp = self.connection.get_groups_for_user(group30["user_id"])
        result = self.assertEqual(resp, res30)
        
    def test_case31(self):
        print "#31. READ groups for a user who is not member of any group"
        resp = self.connection.get_groups_for_user(group31["user_id"])
        result = self.assertEqual(resp, res31)
        
    def test_case32(self):
        print "#32. READ groups for a user who doesn't exist"
        resp = self.connection.get_groups_for_user(group32["user_id"])
        result = self.assertEqual(resp, res32)
    
    def test_case33(self):
        print "#33. READ statuses for a group with at least one status posted"
        resp = self.connection.get_statuses_for_group(group33["group_id"])
        result = self.assertEqual(resp, res33)
    
    def test_case34(self):
        print "#34. READ statuses for a group with no status posted"
        resp = self.connection.get_statuses_for_group(group34["group_id"])
        result = self.assertEqual(resp, res34)

    def test_case35(self):
        print "#35. READ statuses for a group which doesn't exist"
        resp = self.connection.get_statuses_for_group(group35["group_id"])
        result = self.assertEqual(resp, res35)

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()