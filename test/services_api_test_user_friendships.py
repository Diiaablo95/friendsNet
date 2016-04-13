import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

FRIENDSHIP_PROFILE = "/profiles/friendship-profile"

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

class UserFriendshipsTestCase (ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/5/friendships/",
            "links" : [
                {"href" : "/friendsNet/api/users/5/profile/", "rel" : "user profile", "prompt" : "User profile"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/friendships/6/",
                    "data" : [
                        {"name" : "id", "value" : 6, "prompt" : "Friendship id"},
                        {"name" : "user1_id", "value" : 5, "prompt" : "User_1 id"},
                        {"name" : "user2_id", "value" : 6, "prompt" : "User_2 id"},
                        {"name" : "friendship_status", "value" : 1, "prompt" : "Friendship status"},
                        {"name" : "friendship_start", "value" : 800, "prompt" : "Friendship start"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/6/profile/", "rel" : "friend", "prompt" : "Friend profile"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "user2_id", "value" : "", "prompt" : "User_2 id", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/7/friendships/",
            "links" : [
                {"href" : "/friendsNet/api/users/7/profile/", "rel" : "user profile", "prompt" : "User profile"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "user2_id", "value" : "", "prompt" : "User_2 id", "required" : "true"}
                ]
            }
        }
    }

    friendship_post_correct = {
        "template" : {
            "data" : [
                {"name" : "user2_id", "value" : 1}
            ]
        }
    }

    friendship_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "user2_id", "value" : "err"}
            ]
        }
    }

    friendship_user2_not_existing = {
        "template" : {
            "data" : [
                {"name" : "user2_id", "value" : 999}
            ]
        }
    }

    friendship_post_existing = {
        "template" : {
            "data" : [
                {"name" : "user2_id", "value" : 6}
            ]
        }
    }

    def setUp(self):
        super(UserFriendshipsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_friendships, user_id = 5, _external = False)
        self.url_empty = resources.api.url_for(resources.User_friendships, user_id = 7, _external = False)
        self.url_wrong = resources.api.url_for(resources.User_friendships, user_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/1/friendships/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_friendships)

    def test_wrong_url(self):
        #Checks that GET User friendships returns correct status code if given a wrong id
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
    def test_get_friendships(self):
        #Checks that GET Friendship returns correct status code and data format
        print '('+self.test_get_friendships.__name__+')', self.test_get_friendships.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + FRIENDSHIP_PROFILE)

#EMPTY ITEMS
    def test_get_empty_friendships(self):
        print '('+self.test_get_empty_friendships.__name__+')', self.test_get_empty_friendships.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + FRIENDSHIP_PROFILE)

#404
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_friendship(self):
        print '('+self.test_post_friendship.__name__+')', self.test_post_friendship.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.friendship_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_friendship(self):
        print '('+self.test_post_wrong_friendship.__name__+')', self.test_post_wrong_friendship.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.friendship_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404 user1 not existing
    def test_post_not_existing_user1(self):
        print '('+self.test_post_not_existing_user1.__name__+')', self.test_post_not_existing_user1.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.friendship_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 user2 not existing
    def test_post_not_existing_user2(self):
        print '('+self.test_post_not_existing_user2.__name__+')', self.test_post_not_existing_user2.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.friendship_user2_not_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
    def test_post_existing_friendship(self):
        print '('+self.test_post_existing_friendship.__name__+')', self.test_post_existing_friendship.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.friendship_post_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_friendship(self):
        print '('+self.test_post_wrong_header_friendship.__name__+')', self.test_post_wrong_header_friendship.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.friendship_post_correct))
        self.assertEquals(resp.status_code, 415)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()