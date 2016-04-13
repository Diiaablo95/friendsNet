import unittest
import json
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

HAL_JSON = "application/hal+json"
JSON = "application/json"

USER_PROFILE = "/profiles/user-profile"

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Necessary for correct translation in url_for
resources.app.config['SERVER_NAME'] = 'localhost:5000'

#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

class ResourcesAPITestCase(unittest.TestCase):
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting database file.'''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database.'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''Populates the database.'''
        #This method loads the initial values from friendsNet_data_db.sql
        ENGINE.populate_tables()
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        '''
        Remove all records from database.
        '''
        ENGINE.clear()
        self.app_context.pop()

class UserCredentialsTestCase (ResourcesAPITestCase):

    auth_user_credentials = {
        "email" : "email1@gmail.com",
        "password" : "12345678"
    }

    auth_user_token = {
        "token" : "eyJhbGciOiJIUzI1NiIsImV4cCI6MTAwMDAwMDAwMDAwMDAwMDAwMDAxNDYwNTY3MTUxLCJpYXQiOjE0NjA1NjcxNTJ9.eyJpZCI6MX0.t_MuyEEx14LBqbVDeJgFRbnP0DUrwN260-HXbOem_eU"
    }

    resp_auth = {
        "user_id" : 1,
        "token" : "some_value"
    }

    def setUp(self):
        super(UserCredentialsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_authentication, _external = False)

#TEST POST
#201 + MIMETYPE & USER ID WITH EMAIL AND PASSWORD
    def test_authenticate_user_with_credentials(self):
        print '('+self.test_authenticate_user_with_credentials.__name__+')', self.test_authenticate_user_with_credentials.__doc__
        with resources.app.test_client() as client:
            resp = client.post(self.url, data = json.dumps(self.auth_user_credentials), headers = {"Content-Type" : JSON})
            self.assertEquals(resp.status_code, 201)
            data = json.loads(resp.data)

            print data

            self.assertEquals(self.resp_auth["user_id"], data["user_id"])
            self.assertEqual(resp.headers.get("Content-Type", None), JSON)

#201 + MIMETYPE & USER IF WITH TOKEN
    def test_authenticate_user_with_token(self):
        print '('+self.test_authenticate_user_with_token.__name__+')', self.test_authenticate_user_with_token.__doc__
        with resources.app.test_client() as client:
            resp = client.post(self.url, data = json.dumps(self.auth_user_token), headers = {"Content-Type" : JSON})
            self.assertEquals(resp.status_code, 201)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_auth["user_id"], data["user_id"])
            self.assertEqual(resp.headers.get("Content-Type", None), JSON)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()