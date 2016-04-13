import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

CONVERSATION_PROFILE = "/profiles/conversation-profile"

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

class ConversationsTestCase(ResourcesAPITestCase):

    resp_get = {
        "id" : 1,
        "user1_id" : 1,
        "user2_id" : 4,
        "time_last_message" : 950,
        "_links" : {
            "self" : {"href" : "/friendsNet/api/conversations/1/", "profile" : "/profiles/conversation-profile"},
            "user profile" : {"href" : "/friendsNet/api/users/1/profile/"},
            "user contacted profile" : {"href" : "/friendsNet/api/users/4/profile/"},
            "user1 conversations" : {"href" : "/friendsNet/api/users/1/conversations/"},
            "user2 conversations" : {"href" : "/friendsNet/api/users/4/conversations/"},
            "conversation messages" : {"href" : "/friendsNet/api/conversations/1/messages/"}
        }
    }

    def setUp(self):
        super(ConversationsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Conversation, conversation_id = 1, _external = False)
        self.url_wrong = resources.api.url_for(resources.Conversation, conversation_id = 999, _external = False)

#TEST URL
    def test_url(self):
        _url = '/friendsNet/api/conversations/1/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Conversation)

    def test_wrong_url(self):
        resp = self.client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)

        href = data["resource_url"]                         #test HREF
        self.assertEquals(href, self.url_wrong)

        error = data["code"]
        self.assertEquals(error, 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_conversation(self):
        print '('+self.test_get_conversation.__name__+')', self.test_get_conversation.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), HAL_JSON)

#404
    def test_get_not_existing_conversation(self):
        print '('+self.test_get_not_existing_conversation.__name__+')', self.test_get_not_existing_conversation.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST DELETE
#204
    def test_delete_existing_conversation(self):
        print '('+self.test_delete_existing_conversation.__name__+')', self.test_delete_existing_conversation.__doc__
        resp = self.client.delete(self.url, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#404
    def test_delete_not_existing_conversation(self):
        print '('+self.test_delete_not_existing_conversation.__name__+')', self.test_delete_not_existing_conversation.__doc__
        resp = self.client.delete(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
    print 'Start running tests'