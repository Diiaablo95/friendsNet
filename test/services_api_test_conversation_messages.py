import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

MESSAGE_PROFILE = "/profiles/message-profile"

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

class ConversationMessagesTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/conversations/1/messages/",
            "links" : [
                {"href" : "/friendsNet/api/conversations/1/", "rel" : "conversation", "prompt" : "Conversation"},
                {"href" : "/friendsNet/api/users/1/conversations/", "rel" : "user conversations", "prompt" : "User1 conversations"},
                {"href" : "/friendsNet/api/users/4/conversations/", "rel" : "user conversations", "prompt" : "User2 conversations"}
            ],
            "items" : [
                {
                    "data" : [
                        {"name" : "conversation_id", "value" : 1, "prompt" : "Conversation id"},
                        {"name" : "sender_id", "value" : 4, "prompt" : "Sender id"},
                        {"name" : "content", "value" : "Hi :) !", "prompt" : "Message content"},
                        {"name" : "time_sent", "value" : 950, "prompt" : "Time message sent"}
                    ]
                },
                {
                    "data" : [
                        {"name" : "conversation_id", "value" : 1, "prompt" : "Conversation id"},
                        {"name" : "sender_id", "value" : 1, "prompt" : "Sender id"},
                        {"name" : "content", "value" : "Hello :)", "prompt" : "Message content"},
                        {"name" : "time_sent", "value" : 913, "prompt" : "Time message sent"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "sender_id", "value" : "", "prompt" : "Sender id", "required" : "true"},
                    {"name" : "content", "value" : "", "prompt" : "Content", "required" : "true"}
                ]
            }
        }
    }

    message_post_correct = {
        "template" : {
            "data" : [
                {"name" : "sender_id", "value" : 4},
                {"name" : "content", "value" : "Hei"}
            ]
        }
    }

    message_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "sender_id", "value" : 3},
                {"name" : "content", "value" : "Hei"}
            ]
        }
    }

    def setUp(self):
        super(ConversationMessagesTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Conversation_messages, conversation_id = 1, _external = False)
        self.url_wrong = resources.api.url_for(resources.Conversation_messages, conversation_id = 999, _external = False)

    def test_url(self):
        _url = '/friendsNet/api/conversations/1/messages/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Conversation_messages)

    def test_wrong_url(self):
        resp = self.client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)["collection"]

        version = data["version"]                   #test VERSION
        self.assertEquals(version, self.resp_get["collection"]["version"])

        href = data["href"]                         #test HREF
        self.assertEquals(href, self.url_wrong)

        error = data["error"]
        self.assertEquals(error["code"], 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_messages(self):
        print '('+self.test_get_messages.__name__+')', self.test_get_messages.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + MESSAGE_PROFILE)

#404
    def test_get_not_existing_conversation(self):
        print '('+self.test_get_not_existing_conversation.__name__+')', self.test_get_not_existing_conversation.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_message(self):
        print '('+self.test_post_message.__name__+')', self.test_post_message.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.message_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 200)

#403
#sender not one of users of conversation
    def test_post_not_conversation_user(self):
        print '('+self.test_post_not_conversation_user.__name__+')', self.test_post_not_conversation_user.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.message_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 403)

#404
    def test_post_not_existing_conversation(self):
        print '('+self.test_post_not_existing_conversation.__name__+')', self.test_post_not_existing_conversation.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.message_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_post_wrong_header_message(self):
        print '('+self.test_post_wrong_header_message.__name__+')', self.test_post_wrong_header_message.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.message_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()