import unittest
import json
import flask
import friendsNet.resources as resources
import friendsNet.database as database

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"

USER_PROFILE = "/profiles/user-profile"

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

class UserProfileTestCase (ResourcesAPITestCase):

    resp_get = {
        "id" : 1,
                "firstName" : "Antonio",
                "surname" : "Antonino",
                "age" : 20,
                "gender" : 0,
                "_links" : {
                    "self" : {"href" : "/friendsNet/api/users/1/profile/", "profile" : "/profiles/user-profile"},
                    "user comments" : {"href" : "/friendsNet/api/users/1/comments/"},
                    "user memberships" : {"href" : "/friendsNet/api/users/1/groups/"},
                    "user rates" : {"href" : "/friendsNet/api/users/1/rates/"},
                    "user tags" : {"href" : "/friendsNet/api/users/1/tags/"},
                    "user conversations" : {"href" : "/friendsNet/api/users/1/conversations/"},
                    "user friendships" : {"href" : "/friendsNet/api/users/1/friendships/"},
                    "user statuses" : {"href" : "/friendsNet/api/users/1/statuses/"},
                    "user feed" : {"href" : "/friendsNet/api/users/1/feed/"}
                },
                "template" : {
                    "data" : [
                        {"name" : "password", "value" : "", "prompt" : "User password", "required" : "false"},
                        {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "false"},
                        {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                        {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "false"},
                        {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                        {"name" : "age", "value" : "", "prompt" : "User age", "required" : "false"},
                        {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "false"}
                    ]
                }
            }

    profile_patch_correct = {
        "template" : {
            "data" : [
                {"name" : "firstName", "value" : "Michele"}
            ]
        }
    }

    profile_patch_empty = {
        "template" : {
            "data" : []
        }
    }

    profile_patch_incorrect_age = {
        "template" : {
            "data" : [
                {"name" : "age", "value" : -2}
            ]
        }
    }

    profile_patch_incorrect_password = {
        "template" : {
            "data" : [
                {"name" : "password", "value" : "short"}
            ]
        }
    }

    profile_patch_incorrect_prof_picture = {
        "template" : {
            "data" : [
                {"name" : "prof_picture_id", "value" : 999}
            ]
        }
    }

    profile_patch_incorrect_gender = {
        "template" : {
            "data" : [
                {"name" : "gender", "value" : 3}
            ]
        }
    }

    def setUp(self):
        super(UserProfileTestCase, self).setUp()
        self.url = resources.api.url_for(resources.User_profile, user_id = 1, _external = False)
        self.url_wrong = resources.api.url_for(resources.User_profile, user_id = 999, _external = False)

#TEST URL
    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/1/profile/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_profile)

    def test_wrong_url(self):
        resp = self.client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp.status_code, 404)
        data = json.loads(resp.data)

        href = data["resource_url"]                         #test HREF
        self.assertEquals(href, self.url_wrong)

        error = data["code"]
        self.assertEquals(error, 404)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_profile(self):
        print '('+self.test_get_profile.__name__+')', self.test_get_profile.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), HAL_JSON)

#404
    def test_get_not_existing_user(self):
        print '('+self.test_get_not_existing_user.__name__+')', self.test_get_not_existing_user.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_wrong, headers = {"Accept" : HAL_JSON})
            self.assertEquals(resp.status_code, 404)

#TEST PATCH
#204
    def test_patch_profile(self):
        print '('+self.test_patch_profile.__name__+')', self.test_patch_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

        #Check that the title and the body of the message has been modified with the new data
        resp2 = self.client.get(self.url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        new_value = data["firstName"]
        self.assertEquals(new_value, self.profile_patch_correct["template"]["data"][0]["value"])

#PATCH EMPTY
    def test_patch_empty_profile(self):
        #Modify an exisiting friendship and checks that the friendship has been modified correctly in the server
        print '('+self.test_patch_empty_profile.__name__+')', self.test_patch_empty_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_empty), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#400 for incorrect age
    def test_patch_wrong_age_profile(self):
        print '('+self.test_patch_wrong_age_profile.__name__+')', self.test_patch_wrong_age_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_incorrect_age), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 for incorrect gender
    def test_patch_wrong_gender_profile(self):
        print '('+self.test_patch_wrong_gender_profile.__name__+')', self.test_patch_wrong_gender_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_incorrect_gender), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 for incorrect age
    def test_patch_wrong_password_profile(self):
        print '('+self.test_patch_wrong_password_profile.__name__+')', self.test_patch_wrong_password_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_incorrect_password), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 for incorrect age
    def test_patch_wrong_prof_picture_profile(self):
        print '('+self.test_patch_wrong_prof_picture_profile.__name__+')', self.test_patch_wrong_prof_picture_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_incorrect_prof_picture), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#404
    def test_patch_not_existing_user(self):
        print '('+self.test_patch_not_existing_user.__name__+')', self.test_patch_not_existing_user.__doc__
        resp = self.client.patch(self.url_wrong, data = json.dumps(self.profile_patch_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#415
    def test_patch_wrong_header_profile(self):
        print '('+self.test_patch_wrong_header_profile.__name__+')', self.test_patch_wrong_header_profile.__doc__
        resp = self.client.patch(self.url, data = json.dumps(self.profile_patch_correct))
        self.assertEquals(resp.status_code, 415)

#TEST DELETE
#204
    def test_delete_existing_user(self):
        print '('+self.test_delete_existing_user.__name__+')', self.test_delete_existing_user.__doc__
        resp = self.client.delete(self.url, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 204)

#404
    def test_delete_not_existing_user(self):
        #Delete not existing friendship and check response code
        print '('+self.test_delete_not_existing_user.__name__+')', self.test_delete_not_existing_user.__doc__
        resp = self.client.delete(self.url_wrong, headers = {"Accept" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
    print 'Start running tests'