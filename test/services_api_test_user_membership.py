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

class UserMembershipTestCase (ResourcesAPITestCase):

    resp_get = {
        "user_id" : 3,
        "group_id" : 1,
        "administrator" : 0,
        "_links" : {
            "self" : {"href" : "/friendsNet/api/users/3/groups/1/", "profile" : "/profiles/membership-profile"},
            "group members" : {"href" : "/friendsNet/api/groups/1/members/"},
            "user memberships" : {"href" : "/friendsNet/api/users/3/groups/"},
            "user profile" : {"href" : "/friendsNet/api/users/3/profile/"}
        },
        "template" : {
            "data" : [
                {"name" : "administrator", "value" : "", "prompt" : "Membership type", "required" : "false"}
            ]
        }
    }

    membership_patch_correct = {
        "template" : {
            "data" : [
                {"name" : "administrator", "value" : 1}
            ]
        }
    }

    membership_patch_empty = {
        "template" : {
            "data" : []
        }
    }

    membership_patch_incorrect = {
        "template" : {
            "data" : [
                {"name" : "administrator", "value" : 5}
            ]
        }
    }

    def setUp(self):
        super(UserMembershipTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_membership, user_id = 3, group_id = 1, _external = False)
        self.url_wrong_user = resources.api.url_for(resources.User_membership, user_id = 999, group_id = 1,_external = False)
        self.url_wrong_group = resources.api.url_for(resources.User_membership, user_id = 3, group_id = 999,_external = False)
        self.url_wrong_membership = resources.api.url_for(resources.User_membership, user_id = 1, group_id = 3,_external = False)

#TEST URL
    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/3/groups/1/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_membership)

    def test_wrong_url(self):
        #Checks that GET Membership returns correct status code if given a wrong id
        resp = self.client.get(self.url_wrong_membership, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)

        href = data["resource_url"]                         #test HREF
        self.assertEquals(href, self.url_wrong_membership)

        error = data["code"]
        self.assertEquals(error, 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_membership(self):
        #Checks that GET Friendship returns correct status code and data format
        print '('+self.test_get_membership.__name__+')', self.test_get_membership.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), HAL_JSON)

#404 user not existing
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_user, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#404 group not existing
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_group, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#404 user not existing
    def test_get_not_existing_membership(self):
        print '('+self.test_get_not_existing_membership.__name__+')', self.test_get_not_existing_membership.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong_membership, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST PATCH
#204
    def test_patch_membership(self):
        print '('+self.test_patch_membership.__name__+')', self.test_patch_membership.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.membership_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

        resp2 = self.client.get(self.url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        new_value = data["administrator"]
        self.assertEquals(new_value, self.membership_patch_correct["template"]["data"][0]["value"])

#PATCH EMPTY
    def test_patch_empty_membership(self):
        print '('+self.test_patch_empty_membership.__name__+')', self.test_patch_empty_membership.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.membership_patch_empty), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#400
    def test_patch_wrong_membership(self):
        print '('+self.test_patch_wrong_membership.__name__+')', self.test_patch_wrong_membership.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.membership_patch_incorrect), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404 user not existing
    def test_patch_not_existing_user(self):
        #Modify a not exisiting friendship and checks the error returned
        print '('+self.test_patch_not_existing_user.__name__+')', self.test_patch_not_existing_user.__doc__
        resp = self.client.patch(self.url_wrong_user, data = json.dumps(self.membership_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 group not existing
    def test_patch_not_existing_group(self):
        #Modify a not exisiting friendship and checks the error returned
        print '('+self.test_patch_not_existing_group.__name__+')', self.test_patch_not_existing_group.__doc__
        resp = self.client.patch(self.url_wrong_group, data = json.dumps(self.membership_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404 membership not existing
    def test_patch_not_existing_membership(self):
        #Modify a not exisiting friendship and checks the error returned
        print '('+self.test_patch_not_existing_membership.__name__+')', self.test_patch_not_existing_membership.__doc__
        resp = self.client.patch(self.url_wrong_membership, data = json.dumps(self.membership_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_patch_wrong_header_membership(self):
        #Modify an exisiting friendship without specifying the correct header and checks the error returned
        print '('+self.test_patch_wrong_header_membership.__name__+')', self.test_patch_wrong_header_membership.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.membership_patch_correct))
        self.assertEquals(resp.status_code, 415)

#TEST DELETE
#204
    def test_delete_existing_membership(self):
        #Delete existing friendship and check response code
        print '('+self.test_delete_existing_membership.__name__+')', self.test_delete_existing_membership.__doc__
        resp = self.client.delete(self.url, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#404
    def test_delete_not_existing_membership(self):
        #Delete not existing friendship and check response code
        print '('+self.test_delete_not_existing_membership.__name__+')', self.test_delete_not_existing_membership.__doc__
        resp = self.client.delete(self.url_wrong_membership, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
