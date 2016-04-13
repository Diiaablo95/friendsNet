import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

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

class UserStatusesTestCase (ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/2/statuses/",
            "links" : [
                {"href" : "/friendsNet/api/users/2/profile/", "rel" : "author", "prompt" : "Author"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/statuses/3/",
                    "data" : [
                        {"name" : "id", "value" : 3, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 2, "prompt" : "Creator id"},
                        {"name" : "content", "value" : "I'm here!!!!", "prompt" : "Status content"},
                        {"name" : "creation_time", "value" : 90, "prompt" : "Status creation time"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/statuses/3/comments/", "rel" : "status comments", "prompt" : "Status comments"},
                        {"href" : "/friendsNet/api/statuses/3/rates/", "rel" : "status rates", "prompt" : "Status rates"},
                        {"href" : "/friendsNet/api/statuses/3/tags/", "rel" : "status tags", "prompt" : "Status tags"},
                        {"href" : "/friendsNet/api/statuses/3/media/", "rel" : "media list", "prompt" : "Status media items"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/6/statuses/",
            "links" : [
                {"href" : "/friendsNet/api/users/6/profile/", "rel" : "author", "prompt" : "Author"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}
                ]
            }
        }
    }

    status_post_correct = {
        "template" : {
            "data" : [
                {"name" : "content", "value" : "Hello!"}
            ]
        }
    }

    status_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "cont", "value" : "Key wrong!"}
            ]
        }
    }

    def setUp(self):
        super(UserStatusesTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_statuses, user_id = 2, _external = False)
        self.url_empty = resources.api.url_for(resources.User_statuses, user_id = 6, _external = False)
        self.url_wrong = resources.api.url_for(resources.User_statuses, user_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/1/statuses/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_statuses)

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
    def test_get_statuses(self):
        print '('+self.test_get_statuses.__name__+')', self.test_get_statuses.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + STATUS_PROFILE)

#EMPTY ITEMS
    def test_get_empty_statuses(self):
        print '('+self.test_get_empty_statuses.__name__+')', self.test_get_empty_statuses.__doc__
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

#TEST POST
#201
    def test_post_status(self):
        print '('+self.test_post_status.__name__+')', self.test_post_status.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.status_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_status(self):
        print '('+self.test_post_wrong_status.__name__+')', self.test_post_wrong_status.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.status_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_not_existing_user(self):
        print '('+self.test_post_not_existing_user.__name__+')', self.test_post_not_existing_user.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.status_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_post_wrong_header_status(self):
        print '('+self.test_post_wrong_header_status.__name__+')', self.test_post_wrong_header_status.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.status_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()