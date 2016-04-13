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

class GroupStatusesTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/2/statuses/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups", "prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/2/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/2/members/", "group members" : "group members", "prompt" : "Group members"},
                {"href" : "/friendsNet/api/groups/2/requests/", "rel" : "group requests", "prompt" : "Group requests"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/statuses/9/",
                    "data" : [
                        {"name" : "id", "value" : 9, "prompt" : "Status id"},
                        {"name" : "user_id", "value" : 3, "prompt" : "Creator id"},
                        {"name" : "content", "value" : "Hello everyone :)", "prompt" : "Status content"},
                        {"name" : "creation_time", "value" : 1931, "prompt" : "Status creation time"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/statuses/9/comments/", "rel" : "status comments", "prompt" : "Status comments"},
                        {"href" : "/friendsNet/api/statuses/9/rates/", "rel" : "status rates", "prompt" : "Status rates"},
                        {"href" : "/friendsNet/api/statuses/9/tags/", "rel" : "status tags", "prompt" : "Status tags"},
                        {"href" : "/friendsNet/api/statuses/9/media/", "rel" : "status media list", "prompt" : "Status media items"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "Status creator id", "required" : "true"},
                    {"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}
                ]
            }
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/3/statuses/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups", "prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/3/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/3/members/", "group members" : "group members", "prompt" : "Group members"},
                {"href" : "/friendsNet/api/groups/3/requests/", "rel" : "group requests", "prompt" : "Group requests"}
            ],
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "author", "value" : "", "prompt" : "Status creator id", "required" : "true"},
                    {"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}
                ]
            }
        }
    }

    status_post_correct = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 3},
                {"name" : "content", "value" : "Hei!"}
            ]
        }
    }

    status_post_wrong_membership = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 7},
                {"name" : "content", "value" : "Hei!"}
            ]
        }
    }

    status_post_wrong_user = {
        "template" : {
            "data" : [
                {"name" : "author", "value" : 999},
                {"name" : "content", "value" : "Hei!"}
            ]
        }
    }

    def setUp(self):
        super(GroupStatusesTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Group_statuses,group_id = 2, _external = False)
        self.url_empty = resources.api.url_for(resources.Group_statuses, group_id = 3, _external = False)
        self.url_wrong = resources.api.url_for(resources.Group_statuses, group_id = 999, _external = False)

    def test_url(self):
        _url = '/friendsNet/api/groups/2/statuses/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Group_statuses)

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
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
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

#403 wrong membership
    def test_post_not_member_group(self):
        print '('+self.test_post_not_member_group.__name__+')', self.test_post_not_member_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.status_post_wrong_membership), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 403)

#404 group not existing
    def test_post_not_existing_group(self):
        print '('+self.test_post_not_existing_group.__name__+')', self.test_post_not_existing_group.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.status_post_wrong_membership), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 user not existing
    def test_post_not_existing_user(self):
        print '('+self.test_post_not_existing_user.__name__+')', self.test_post_not_existing_user.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.status_post_wrong_user), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_post_wrong_header_status(self):
        print '('+self.test_post_wrong_header_status.__name__+')', self.test_post_wrong_header_status.__doc__
        resp = self.client.post(self.url_wrong, data = json.dumps(self.status_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()