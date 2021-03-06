import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

GROUP_MEMBERSHIP_PROFILE = "/profiles/membership-profile"

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

class UserMembershipsTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/1/groups/",
            "links" : [
                {"href" : "/friendsNet/api/users/1/profile/", "rel" : "user profile", "prompt" : "User profile"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/users/1/groups/1/",
                    "data" : [
                        {"name" : "id", "value" : 1, "prompt" : "User id"},
                        {"name" : "group_id", "value" : 1, "prompt" : "Group id"},
                        {"name" : "administrator", "value" : 1, "prompt" : "Membership type"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/groups/1/", "rel" : "group", "prompt" : "Group"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "group_id", "value" : "", "prompt" : "Group id", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/6/groups/",
            "links" : [
                {"href" : "/friendsNet/api/users/6/profile/", "rel" : "user profile", "prompt" : "User profile"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "group_id", "value" : "", "prompt" : "Group id", "required" : "true"}
                ]
            }
        }
    }

    membership_post_correct = {
        "template" : {
            "data" : [
                {"name" : "group_id", "value" : 2}
            ]
        }
    }

    membership_post_group_wrong = {
        "template" : {
            "data" : [
                {"name" : "group_id", "value" : 28}
            ]
        }
    }

    membership_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "group_id", "value" : "err"}
            ]
        }
    }

    membership_post_existing = {
        "template" : {
            "data" : [
                {"name" : "group_id", "value" : 1}
            ]
        }
    }

    def setUp(self):
        super(UserMembershipsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_memberships, user_id = 1, _external = False)
        self.url_empty = resources.api.url_for(resources.User_memberships, user_id = 6, _external = False)
        self.url_wrong = resources.api.url_for(resources.User_memberships, user_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/1/groups/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_memberships)

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
    def test_get_memberships(self):
        print '('+self.test_get_memberships.__name__+')', self.test_get_memberships.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_PROFILE)

#EMPTY ITEMS
    def test_get_empty_memberships(self):
        print '('+self.test_get_empty_memberships.__name__+')', self.test_get_empty_memberships.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_PROFILE)

#404
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_membership(self):
        print '('+self.test_post_membership.__name__+')', self.test_post_membership.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.membership_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_membership(self):
        print '('+self.test_post_wrong_membership.__name__+')', self.test_post_wrong_membership.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.membership_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404 user not existing
    def test_post_not_existing_user(self):
        print '('+self.test_post_not_existing_user.__name__+')', self.test_post_not_existing_user.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.membership_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 group not existing
    def test_post_not_existing_group(self):
        print '('+self.test_post_not_existing_group.__name__+')', self.test_post_not_existing_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.membership_post_group_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
    def test_post_existing_membership(self):
        print '('+self.test_post_existing_membership.__name__+')', self.test_post_existing_membership.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.membership_post_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_membership(self):
        print '('+self.test_post_wrong_header_membership.__name__+')', self.test_post_wrong_header_membership.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.membership_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()