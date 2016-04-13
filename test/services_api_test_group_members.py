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

class MembershipTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/2/members/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups","prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/2/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/2/requests/", "group requests" : "group requests", "prompt" : "Group requests"},
                {"href" : "/friendsNet/api/groups/2/statuses/", "rel" : "group statuses", "prompt" : "Group statuses"}
            ],
            "items" : [
                {
                    "href" : "/friendsNet/api/users/3/groups/2/",
                    "data" : [
                        {"name" : "id", "value" : 3, "prompt" : "User id"},
                        {"name" : "group_id", "value" : 2, "prompt" : "Group id"},
                        {"name" : "administrator", "value" : 1, "prompt" : "Membership type"}
                    ]
                }
            ]
        }
    }

    resp_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/groups/3/members/",
            "links" : [
                {"href" : "/friendsNet/api/groups/", "rel" : "groups","prompt" : "Groups"},
                {"href" : "/friendsNet/api/groups/3/", "rel" : "group", "prompt" : "Group"},
                {"href" : "/friendsNet/api/groups/3/requests/", "group requests" : "group requests", "prompt" : "Group requests"},
                {"href" : "/friendsNet/api/groups/3/statuses/", "rel" : "group statuses", "prompt" : "Group statuses"}
            ],
            "items" : []
        }
    }

    def setUp(self):
        super(MembershipTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Group_members, group_id = 2, _external = False)
        self.url_wrong = resources.api.url_for(resources.Group_members, group_id = 999, _external = False)

#TEST URL
    def test_url(self):
        _url = '/friendsNet/api/groups/2/members/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Group_members)

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
    def test_get_members(self):
        print '('+self.test_get_members.__name__+')', self.test_get_members.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_PROFILE)


#404
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
    print 'Start running tests'