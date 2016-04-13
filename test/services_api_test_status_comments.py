import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

COMMENT_PROFILE = "/profiles/comment-profile"

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

class StatusCommentsTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/4/comments/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/4/", "rel" : "status", "prompt" : "Status commented"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/comments/6/",
                    "data" : [
                        {"name" : "id", "value" : 6, "prompt" : "Comment id"},
                        {"name" : "status_id", "value" : 4, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 1, "prompt" : "User id"},
                        {"name" : "content", "value" : "Hello :D !", "prompt" : "Comment content"},
                        {"name" : "creation_time", "value" : 120, "prompt" : "Comment creation time"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/1/profile/", "rel" : "author", "prompt" : "User profile"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                    {"name" : "content", "value" : "", "prompt" : "Content", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/statuses/6/comments/",
            "links" : [
                {"href" : "/friendsNet/api/statuses/6/", "rel" : "status", "prompt" : "Status commented"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                    {"name" : "content", "value" : "", "prompt" : "Content", "required" : "true"}
                ]
            }
        }
    }

    comment_post_correct = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 3},
                {"name" : "content", "value" : "ahah"}
            ]
        }
    }

    comment_post_wrong = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 3}    #With no content
            ]
        }
    }

    def setUp(self):
        super(StatusCommentsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Status_comments, status_id = 4, _external = False)
        self.url_empty = resources.api.url_for(resources.Status_comments, status_id = 6, _external = False)
        self.url_wrong = resources.api.url_for(resources.Status_comments, status_id = 999, _external = False)

    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/statuses/4/comments/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Status_comments)

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
    def test_get_comments(self):
        print '('+self.test_get_comments.__name__+')', self.test_get_comments.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + COMMENT_PROFILE)

#EMPTY ITEMS
    def test_get_empty_comments(self):
        print '('+self.test_get_empty_comments.__name__+')', self.test_get_empty_comments.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_empty, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_empty, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + COMMENT_PROFILE)

#404
    def test_get_not_existing_status(self):
        print '('+self.test_get_not_existing_status.__name__+')', self.test_get_not_existing_status.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST POST
#201
    def test_post_comment(self):
        print '('+self.test_post_comment.__name__+')', self.test_post_comment.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.comment_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_comment(self):
        print '('+self.test_post_wrong_comment.__name__+')', self.test_post_wrong_comment.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.comment_post_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_not_existing_status(self):
        print '('+self.test_post_not_existing_status.__name__+')', self.test_post_not_existing_status.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.comment_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_post_wrong_header_comment(self):
        print '('+self.test_post_wrong_header_comment.__name__+')', self.test_post_wrong_header_comment.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.comment_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()