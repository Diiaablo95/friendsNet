import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"

STATUS_PROFILE = "/profiles/status-profile"

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

class UserTagsTestCase (ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/4/tags/",
            "links" : [
                {"href" : "/friendsNet/api/users/4/profile/", "rel" : "tag", "prompt" : "User profile"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/statuses/1/",
                    "data" : [
                        {"name" : "id", "value" : 1, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 1, "prompt" : "Creator id"},
                        {"name" : "content", "value" : "Good morning!", "prompt" : "Status content"},
                        {"name" : "creation_time", "value" : 50, "prompt" : "Status creation time"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/statuses/1/comments/", "rel" : "status comments", "prompt" : "Status comments"},
                        {"href" : "/friendsNet/api/statuses/1/rates/", "rel" : "status rates", "prompt" : "Status rates"},
                        {"href" : "/friendsNet/api/statuses/1/tags/", "rel" : "status tags", "prompt" : "Status tags"},
                        {"href" : "/friendsNet/api/statuses/1/media/", "rel" : "media list", "prompt" : "Status media items"}
                    ]
                }
            ]
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/6/tags/",
            "links" : [
                {"href" : "/friendsNet/api/users/6/profile/", "rel" : "tag", "prompt" : "User profile"}
            ],
            "items" : []
        }
    }

    def setUp(self):
        super(UserTagsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_tags, user_id = 4, _external = False)
        self.url_empty = resources.api.url_for(resources.User_tags, user_id = 6, _external = False)
        self.url_wrong = resources.api.url_for(resources.User_tags, user_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/6/tags/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_tags)

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
    def test_get_tags(self):
        print '('+self.test_get_tags.__name__+')', self.test_get_tags.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + STATUS_PROFILE)

#EMPTY ITEMS
    def test_get_empty_tags(self):
        print '('+self.test_get_empty_tags.__name__+')', self.test_get_empty_tags.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + STATUS_PROFILE)

#404
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()