import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

GROUP_MEMBERSHIP_REQUEST_PROFILE = "/profiles/request-profile"

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

class GroupRequestsTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/2/requests/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups", "prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/2/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/2/members/", "group members" : "group members", "prompt" : "Group members"},
                {"href" : "/friendsNet/api/groups/2/statuses/", "rel" : "group statuses", "prompt" : "Group statuses"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/groups/2/requests/1/",
                    "data" : [
                        {"name" : "id", "value" : 2, "prompt" : "Group id"},
                        {"name" : "user_id", "value" : 1, "prompt" : "User id"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/1/profile/", "rel" : "user profile", "prompt" : "User profile",},
                        {"href" : "/friendsNet/api/users/1/groups/", "rel" : "user memberships", "prompt" : "User memberships"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/groups/2/requests/4/",
                    "data" : [
                        {"name" : "id", "value" : 2, "prompt" : "Group id"},
                        {"name" : "user_id", "value" : 4, "prompt" : "User id"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/4/profile/", "rel" : "user profile", "prompt" : "User profile"},
                        {"href" : "/friendsNet/api/users/4/groups/", "rel" : "user memberships", "prompt" : "User memberships"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "user_id", "value" : "", "prompt" : "User requesting id", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/3/requests/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups", "prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/3/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/3/members/", "group members" : "group members", "prompt" : "Group members"},
                {"href" : "/friendsNet/api/groups/3/statuses/", "rel" : "group statuses", "prompt" : "Group statuses"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "user_id", "value" : "", "prompt" : "User requesting id", "required" : "true"}
                ]
            }
        }
    }

    request_post_correct = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : 5}
            ]
        }
    }

    request_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : "err"}
            ]
        }
    }

    request_post_existing_request = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : 1}
            ]
        }
    }

    request_post_existing_member = {
        "template" : {
            "data" : [
                {"name" : "user_id", "value" : 3}
            ]
        }
    }

    def setUp(self):
        super(GroupRequestsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Group_requests,group_id = 2, _external = False)
        self.url_empty = resources.api.url_for(resources.Group_requests, group_id = 3, _external = False)
        self.url_wrong_privacy = resources.api.url_for(resources.Group_requests, group_id = 1, _external = False)
        self.url_wrong = resources.api.url_for(resources.Group_requests, group_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/groups/2/requests/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Group_requests)

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
    def test_get_requests(self):
        print '('+self.test_get_requests.__name__+')', self.test_get_requests.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_REQUEST_PROFILE)

#EMPTY ITEMS
    def test_get_empty_requests(self):
        print '('+self.test_get_empty_requests.__name__+')', self.test_get_empty_requests.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_REQUEST_PROFILE)

#404
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_request(self):
        print '('+self.test_post_request.__name__+')', self.test_post_request.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.request_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_privacy_group(self):
        print '('+self.test_post_wrong_privacy_group.__name__+')', self.test_post_wrong_privacy_group.__doc__
        resp = self.client.post(self.url_wrong_privacy, data = json.dumps(self.request_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_not_existing_group(self):
        print '('+self.test_post_not_existing_group.__name__+')', self.test_post_not_existing_group.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.request_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
#request existing for the user to the group
    def test_post_request_existing_request(self):
        print '('+self.test_post_request_existing_request.__name__+')', self.test_post_request_existing_request.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.request_post_existing_request), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#409
#user already member of the group
    def test_post_request_existing_membership(self):
        print '('+self.test_post_request_existing_membership.__name__+')', self.test_post_request_existing_membership.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.request_post_existing_member), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_request(self):
        print '('+self.test_post_wrong_header_request.__name__+')', self.test_post_wrong_header_request.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.request_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()