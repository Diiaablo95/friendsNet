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

class GroupRequestTestCase(ResourcesAPITestCase):

    resp_get = {
        "id" : 2,
        "user_id" : 1,
        "_links" : {
            "self" : {"href" : "/friendsNet/api/groups/2/requests/1/", "profile" : "/profiles/request-profile"},
            "groups" : {"href" : "/friendsNet/api/groups/"},
            "group statuses" : {"href" : "/friendsNet/api/groups/2/statuses/"},
            "group members" : {"href" : "/friendsNet/api/groups/2/members/"},
            "group" : {"href" : "/friendsNet/api/groups/2/"},
            "user profile" : {"href" : "/friendsNet/api/users/1/profile/"},
            "user memberships" : {"href" : "/friendsNet/api/users/1/groups/"}
        },
        "template" : {
            "data" : [
                {"name" : "status", "value" : "", "prompt" : "Request status", "required" : "false"}
            ]
        }
    }

    request_accept_correct = {
        "template" : {
            "data" : [
                {"name" : "status", "value" : 1}
            ]
        }
    }

    request_decline_correct = {
        "template" : {
            "data" : [
                {"name" : "status", "value" : 0}
            ]
        }
    }

    request_patch_empty = {
        "template" : {
            "data" : []
        }
    }

    request_patch_incorrect = {
        "template" : {
            "data" : [
                {"name" : "status", "value" : 3}
            ]
        }
    }

    def setUp(self):
        super(GroupRequestTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Group_request, group_id = 2, user_id = 1, _external = False)
        self.url_wrong_group = resources.api.url_for(resources.Group_request, group_id  = 999, user_id = 4, _external = False)
        self.url_wrong_user = resources.api.url_for(resources.Group_request, group_id  = 2, user_id = 999, _external = False)
        self.url_wrong_request = resources.api.url_for(resources.Group_request, group_id = 2, user_id = 3, _external = False)
        self.url_existing_membership = resources.api.url_for(resources.Group_request, group_id = 1, user_id = 1, _external = False)

#TEST URL
    def test_url(self):
        _url = '/friendsNet/api/groups/2/requests/1/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Group_request)

    def test_wrong_url(self):
        resp = self.client.get(self.url_wrong_request, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)

        href = data["resource_url"]                         #test HREF
        self.assertEquals(href, self.url_wrong_request)

        error = data["code"]
        self.assertEquals(error, 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_request(self):
        print '('+self.test_get_request.__name__+')', self.test_get_request.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), HAL_JSON)

#404
#group not existing
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_group, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#404
#user not existing
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_user, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#404
#request not existing
    def test_get_not_existing_request(self):
        print '('+self.test_get_not_existing_request.__name__+')', self.test_get_not_existing_request.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_request, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST PATCH
#201 accept
    def test_accept_request(self):
        print '('+self.test_accept_request.__name__+')', self.test_accept_request.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.request_accept_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]

        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#201 decline
    def test_decline_request(self):
        print '('+self.test_decline_request.__name__+')', self.test_decline_request.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.request_decline_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

#PATCH EMPTY
    def test_patch_empty_request(self):
        print '('+self.test_patch_empty_request.__name__+')', self.test_patch_empty_request.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.request_patch_empty), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

#400
    def test_patch_wrong_request(self):
        print '('+self.test_patch_wrong_request.__name__+')', self.test_patch_wrong_request.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.request_patch_incorrect), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404 group wrong
    def test_patch_not_existing_group(self):
        print '('+self.test_patch_not_existing_group.__name__+')', self.test_patch_not_existing_group.__doc__
        resp = self.client.patch(self.url_wrong_group, data = json.dumps(self.request_accept_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 request wrong
    def test_patch_not_existing_request(self):
        print '('+self.test_patch_not_existing_request.__name__+')', self.test_patch_not_existing_request.__doc__
        resp = self.client.patch(self.url_wrong_request, data = json.dumps(self.request_accept_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_patch_wrong_header_request(self):
        print '('+self.test_patch_wrong_header_request.__name__+')', self.test_patch_wrong_header_request.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.request_accept_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    unittest.main()
    print 'Start running tests'