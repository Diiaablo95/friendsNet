import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

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

class StatusTagsTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/4/tags/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/4/", "rel" : "status", "prompt" : "Status"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/users/1/profile/",
                    "data" : [
                        {"name" : "id", "value" : 1, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Antonio", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Antonino", "prompt" : "User surname"},
                        {"name" : "age", "value" : 20, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/statuses/4/tags/1/", "rel" : "status tag", "prompt" : "Status tag"},
                        {"href" : "/friendsNet/api/users/1/tags/", "rel" : "user tags", "prompt" : "User tags"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/2/profile/",
                    "data" : [
                        {"name" : "id", "value" : 2, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Eugenio", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Leonetti", "prompt" : "User surname"},
                        {"name" : "age", "value" : 25, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/statuses/4/tags/2/", "rel" : "status tag", "prompt" : "Status tag"},
                        {"href" : "/friendsNet/api/users/2/tags/", "rel" : "user tags", "prompt" : "User tags"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "user_id", "value" : "", "prompt" : "User tagged", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/7/tags/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/7/", "rel" : "status", "prompt" : "Status"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "user_id", "value" : "", "prompt" : "User tagged", "required" : "true"}
                ]
            }
        }
    }

    tag_post_correct = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : 3}
            ]
        }
    }

    tag_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : "rel"}
            ]
        }
    }

    tag_post_existing = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : 1}
            ]
        }
    }

    def setUp(self):
        super(StatusTagsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Status_tags, status_id = 4, _external = False)
        self.url_empty = resources.api.url_for(resources.Status_tags, status_id = 7, _external = False)
        self.url_wrong = resources.api.url_for(resources.Status_tags, status_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/statuses/4/tags/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Status_tags)

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
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + USER_PROFILE)

#EMPTY ITEMS
    def test_get_empty_tags(self):
        print '('+self.test_get_empty_tags.__name__+')', self.test_get_empty_tags.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + USER_PROFILE)

#404
    def test_get_not_existing_status(self):
        print '('+self.test_get_not_existing_status.__name__+')', self.test_get_not_existing_status.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_tag(self):
        print '('+self.test_post_tag.__name__+')', self.test_post_tag.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.tag_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_tag(self):
        print '('+self.test_post_wrong_tag.__name__+')', self.test_post_wrong_tag.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.tag_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_not_existing_status(self):
        print '('+self.test_post_not_existing_status.__name__+')', self.test_post_not_existing_status.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.tag_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
    def test_post_existing_tag(self):
        print '('+self.test_post_existing_tag.__name__+')', self.test_post_existing_tag.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.tag_post_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_tag(self):
        print '('+self.test_post_wrong_header_tag.__name__+')', self.test_post_wrong_header_tag.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.tag_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()