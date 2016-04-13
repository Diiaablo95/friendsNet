import unittest
import json
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

class GroupsTestCase(ResourcesAPITestCase):

    group_post_correct = {
        "template" : {
            "data" : [
                {"name" : "name", "value" : "New group"},
                {"name" : "privacy_level", "value" : 1},
                {"name" : "description", "value" : "Group just because."}
            ]
        }
    }

    group_post_wrong_privacy_level = {
        "template" : {
            "data" : [
                {"name" : "name", "value" : "err group"},
                {"name" : "privacy_level", "value" : -1},
                {"name" : "description", "value" : "Group just because."}
            ]
        }
    }

    group_post_wrong_prof_picture = {
        "template" : {
            "data" : [
                {"name" : "name", "value" : "err group"},
                {"name" : "privacy_level", "value" : -1},
                {"name" : "prof_picture_id", "value" : 999}
            ]
        }
    }

    def setUp(self):
        super(GroupsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Groups, _external = False)

    '''
    def test_url(self):
        _url = "/friendsNet/api/groups/"
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Groups)
    '''

#TEST POST
#201
    def test_post_group(self):
        print '('+self.test_post_group.__name__+')', self.test_post_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.group_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_wrong_privacy_level_group(self):
        print '('+self.test_post_wrong_privacy_level_group.__name__+')', self.test_post_wrong_privacy_level_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.group_post_wrong_privacy_level), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404
    def test_post_wrong_prof_picture_group(self):
        print '('+self.test_post_wrong_prof_picture_group.__name__+')', self.test_post_wrong_prof_picture_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.group_post_wrong_prof_picture), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#415
    def test_post_wrong_header_group(self):
        print '('+self.test_post_wrong_header_group.__name__+')', self.test_post_wrong_header_group.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.group_post_correct))
        self.assertEquals(resp.status_code, 415)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()