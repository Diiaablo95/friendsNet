import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

GROUP_PROFILE = "/profiles/group-profile"

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

class GroupTestCase(ResourcesAPITestCase):

    resp_get = {
        "id" : 3,
        "name" : "Group3",
        "privacy_level" : 2,
        "description" : "Opennn",
        "_links" : {
            "self" : {"href" : "/friendsNet/api/groups/3/", "profile" : "/profiles/group-profile"},
            "groups" : {"href" : "/friendsNet/api/groups/"},
            "group statuses" : {"href" : "/friendsNet/api/groups/3/statuses/"},
            "group members" : {"href" : "/friendsNet/api/groups/3/members/"},
            "group requests" : {"href" : "/friendsNet/api/groups/3/requests/"}
        },
        "template" : {
            "data" : [
                {"name" : "name", "value" : "", "prompt" : "Group name", "required" : "false"},
                {"name" : "privacy_level", "value" : "", "prompt" : "Privacy_level", "required" : "false"},
                {"name" : "description", "value" : "", "prompt" : "Description", "required" : "false"},
                {"name" : "prof_picture_id", "value" : "", "prompt" : "Prof picture id", "required" : "false"}
            ]
        }
    }

    group_patch_correct = {
        "template" : {
            "data" : [
                {"name" : "name", "value" : "Arrrg"}
            ]
        }
    }

    group_patch_empty = {
        "template" : {
            "data" : []
        }
    }

    group_patch_incorrect_privacy_level = {
        "template" : {
            "data" : [
                {"name" : "privacy_level", "value" : 5}
            ]
        }
    }

    group_patch_incorrect_privacy_prof_picture = {
        "template" : {
            "data" : [
                {"name" : "prof_picture_id", "value" : 999}
            ]
        }
    }

    def setUp(self):
        super(GroupTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Group, group_id = 3, _external = False)
        self.url_wrong = resources.api.url_for(resources.Group, group_id = 999, _external = False)

#TEST URL
    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/groups/3/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Group)

    def test_wrong_url(self):
        #Checks that GET Friendship returns correct status code if given a wrong id
        resp = self.client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)

        href = data["resource_url"]                         #test HREF
        self.assertEquals(href, self.url_wrong)

        error = data["code"]
        self.assertEquals(error, 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_group(self):
        print '('+self.test_get_group.__name__+')', self.test_get_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), HAL_JSON)


#404
    def test_get_not_existing_group(self):
        print '('+self.test_get_not_existing_group.__name__+')', self.test_get_not_existing_group.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST PATCH
#204
    def test_patch_group(self):
        print '('+self.test_patch_group.__name__+')', self.test_patch_group.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.group_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

        #Check that the title and the body of the message has been modified with the new data
        resp2 = self.client.get(self.url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        new_value = data["name"]
        self.assertEquals(new_value, self.group_patch_correct["template"]["data"][0]["value"])

#PATCH EMPTY
    def test_patch_empty_group(self):
        print '('+self.test_patch_empty_group.__name__+')', self.test_patch_empty_group.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.group_patch_empty), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#400 privacy level wrong
    def test_patch_wrong_privacy_level_group(self):
        print '('+self.test_patch_wrong_privacy_level_group.__name__+')', self.test_patch_wrong_privacy_level_group.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.group_patch_incorrect_privacy_level), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 profile picture id wrong
    def test_patch_wrong_prof_picture_group(self):
        print '('+self.test_patch_wrong_prof_picture_group.__name__+')', self.test_patch_wrong_prof_picture_group.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.group_patch_incorrect_privacy_prof_picture), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404
    def test_patch_not_existing_group(self):
        print '('+self.test_patch_not_existing_group.__name__+')', self.test_patch_not_existing_group.__doc__
        resp = self.client.patch(self.url_wrong, data = json.dumps(self.group_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_patch_wrong_header_group(self):
        print '('+self.test_patch_wrong_header_group.__name__+')', self.test_patch_wrong_header_group.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.group_patch_correct))
        self.assertEquals(resp.status_code, 415)

#TEST DELETE
#204
    def test_delete_existing_group(self):
        print '('+self.test_delete_existing_group.__name__+')', self.test_delete_existing_group.__doc__
        resp = self.client.delete(self.url, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#404
    def test_delete_not_existing_group(self):
        print '('+self.test_delete_not_existing_group.__name__+')', self.test_delete_not_existing_group.__doc__
        resp = self.client.delete(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
    print 'Start running tests'