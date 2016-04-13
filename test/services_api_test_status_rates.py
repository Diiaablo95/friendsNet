import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

RATE_PROFILE = "/profiles/rate-profile"

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

class StatusRatesTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/4/rates/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/4/", "rel" : "status", "prompt" : "Status rated"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/rates/6/",
                    "data" : [
                        {"name" : "id", "value" : 6, "prompt" : "Rate id"},
                        {"name" : "status_id", "value" : 4, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 2, "prompt" : "User id"},
                        {"name" : "rate", "value" : 4, "prompt" : "Rate value"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/2/profile/", "rel" : "author", "prompt" : "User profile"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/rates/5/",
                    "data" : [
                        {"name" : "id", "value" : 5, "prompt" : "Rate id"},
                        {"name" : "status_id", "value" : 4, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 3, "prompt" : "User id"},
                        {"name" : "rate", "value" : 4, "prompt" : "Rate value"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/3/profile/", "rel" : "author", "prompt" : "User profile"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/rates/4/",
                    "data" : [
                        {"name" : "id", "value" : 4, "prompt" : "Rate id"},
                        {"name" : "status_id", "value" : 4, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 4, "prompt" : "User id"},
                        {"name" : "rate", "value" : 4, "prompt" : "Rate value"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/4/profile/", "rel" : "author", "prompt" : "User profile"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                    {"name" : "rate", "value" : "", "prompt" : "Rate", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/3/rates/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/3/", "rel" : "status", "prompt" : "Status rated"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                    {"name" : "rate", "value" : "", "prompt" : "Rate", "required" : "true"}
                ]
            }
        }
    }

    rate_post_correct = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 1},
                {"name" : "rate", "value" : 1}
            ]
        }
    }

    rate_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 1},
                {"name" : "rate", "value" : "aweq"}
            ]
        }
    }

    rate_post_existing = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 3},
                {"name" : "rate", "value" : 1}
            ]
        }
    }

    def setUp(self):
        super(StatusRatesTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Status_rates, status_id = 4, _external = False)
        self.url_empty = resources.api.url_for(resources.Status_rates, status_id = 3, _external = False)
        self.url_wrong = resources.api.url_for(resources.Status_rates, status_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/statuses/4/rates/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Status_rates)

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
    def test_get_rates(self):
        print '('+self.test_get_rates.__name__+')', self.test_get_rates.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + RATE_PROFILE)

#EMPTY ITEMS
    def test_get_empty_rates(self):
        print '('+self.test_get_empty_rates.__name__+')', self.test_get_empty_rates.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + RATE_PROFILE)

#404
    def test_get_not_existing_status(self):
        print '('+self.test_get_not_existing_status.__name__+')', self.test_get_not_existing_status.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_rate(self):
        print '('+self.test_post_rate.__name__+')', self.test_post_rate.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.rate_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_rate(self):
        print '('+self.test_post_wrong_rate.__name__+')', self.test_post_wrong_rate.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.rate_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_not_existing_status(self):
        print '('+self.test_post_not_existing_status.__name__+')', self.test_post_not_existing_status.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.rate_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
    def test_post_existing_rate(self):
        print '('+self.test_post_existing_rate.__name__+')', self.test_post_existing_rate.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.rate_post_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_rate(self):
        print '('+self.test_post_wrong_header_rate.__name__+')', self.test_post_wrong_header_rate.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.rate_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()