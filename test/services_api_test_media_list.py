import unittest
import os
import friendsNet.resources as resources
import friendsNet.database as database
from StringIO import StringIO

DB_PATH = 'db/friendsNet_test.db'
ENGINE = database.Engine(DB_PATH)

#HAL_JSON = "application/hal+json"
MULTIPART = "multipart/form-data"

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Necessary for correct translation in url_for
resources.app.config['SERVER_NAME'] = 'localhost:5000'

#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

test_image_url = "test/trial_image.jpg"
test_image_name = "trial_image.jpg"

new_created_test_image_url = "friendsNet/media_uploads/media11.jpg"


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
        ENGINE.populate_tables()
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        ENGINE.clear()
        self.app_context.pop()

        try:
            os.remove(new_created_test_image_url)
        except:
            pass

class MediaListTestCase(ResourcesAPITestCase):

    def setUp(self):
        super(MediaListTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Media_list, _external = False)

#TEST POST
#200
    def test_post(self):
        print '('+self.test_post.__name__+')', self.test_post.__doc__
        with open(test_image_url, 'rb') as img:
            imgStringIO = StringIO(img.read())

        resp = self.client.post(self.url, headers = {"Content-Type" : MULTIPART}, data = {"file": (imgStringIO, test_image_name)})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url)
        self.assertEquals(resp2.status_code, 200)

#400
    def test_post_bad(self):
        print '('+self.test_post_bad.__name__+')', self.test_post_bad.__doc__
        with open(test_image_url, 'rb') as img:
            imgStringIO = StringIO(img.read())

        resp = self.client.post(self.url, headers = {"Content-Type" : MULTIPART})
        self.assertEquals(resp.status_code, 400)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()