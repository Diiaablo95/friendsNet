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

class UserProfilesTestCase(ResourcesAPITestCase):

    resp_get = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/",
            "items" : [
                {
                    "href" : "/friendsNet/api/users/1/profile/",
                    "data" : [
                        {"name" : "id", "value" : 1, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Antonio", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Antonino", "prompt" : "User surname"},
                        {"name" : "age", "value" : 20, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/1/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/1/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/1/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/1/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/1/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/1/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/1/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/1/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/2/profile/",
                    "data" : [
                        {"name" : "id", "value" : 2, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Eugenio", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Leonetti", "prompt" : "User surname"},
                        {"name" : "age", "value" : 25, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/2/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/2/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/2/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/2/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/2/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/2/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/2/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/2/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/3/profile/",
                    "data" : [
                        {"name" : "id", "value" : 3, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Mikko", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Yliniemi", "prompt" : "User surname"},
                        {"name" : "age", "value" : 28, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/3/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/3/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/3/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/3/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/3/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/3/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/3/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/3/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/4/profile/",
                    "data" : [
                        {"name" : "id", "value" : 4, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Stefany", "prompt" : "User first name"},
                        {"name" : "middle_name", "value" : "Katherine", "prompt" : "User middle name"},
                        {"name" : "surname", "value" : "Smith", "prompt" : "User surname"},
                        {"name" : "age", "value" : 15, "prompt" : "User age"},
                        {"name" : "gender", "value" : 1, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/4/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/4/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/4/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/4/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/4/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/4/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/4/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/4/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/5/profile/",
                    "data" : [
                        {"name" : "id", "value" : 5, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Mickael", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Red", "prompt" : "User surname"},
                        {"name" : "age", "value" : 17, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/5/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/5/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/5/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/5/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/5/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/5/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/5/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/5/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/6/profile/",
                    "data" : [
                        {"name" : "id", "value" : 6, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Trial", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "User", "prompt" : "User surname"},
                        {"name" : "age", "value" : 15, "prompt" : "User age"},
                        {"name" : "gender", "value" : 1, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/6/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/6/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/6/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/6/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/6/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/6/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/6/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/6/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                },
                {
                    "href" : "/friendsNet/api/users/7/profile/",
                    "data" : [
                        {"name" : "id", "value" : 7, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "User", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Trial", "prompt" : "User surname"},
                        {"name" : "age", "value" : 82, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/7/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/7/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/7/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/7/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/7/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/7/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/7/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/7/feed/", "rel" : "user feed", "prompt" : "User feed"},
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "email", "value" : "", "prompt" : "User email", "required" : "true"},
                    {"name" : "password", "value" : "", "prompt" : "User password", "required" : "true"},
                    {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "true"},
                    {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                    {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "true"},
                    {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                    {"name" : "age", "value" : "", "prompt" : "User age", "required" : "true"},
                    {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "true"}
                ]
            },
            "queries" : [
                {
                    "href" : "/friendsNet/api/users/",
                    "rel" : "search",
                    "prompt" : "Search user",
                    "data" : [
                        {"name" : "name", "value" : ""},
                        {"name" : "surname", "value" : ""}
                    ]
                }
            ]
        }
    }

    resp_get_empty = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/",
            "items" : [],
            "template" : {
                "data" : [
                    {"name" : "email", "value" : "", "prompt" : "User email", "required" : "true"},
                    {"name" : "password", "value" : "", "prompt" : "User password", "required" : "true"},
                    {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "true"},
                    {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                    {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "true"},
                    {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                    {"name" : "age", "value" : "", "prompt" : "User age", "required" : "true"},
                    {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "true"}
                ]
            },
            "queries" : [
                {
                    "href" : "/friendsNet/api/users/",
                    "rel" : "search",
                    "prompt" : "Search user",
                    "data" : [
                        {"name" : "name", "value" : ""},
                        {"name" : "surname", "value" : ""}
                    ]
                }
            ]
        }
    }

    resp_get_name_query = {
                "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/",
            "items" : [
                {
                    "href" : "/friendsNet/api/users/6/profile/",
                    "data" : [
                        {"name" : "id", "value" : 6, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Trial", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "User", "prompt" : "User surname"},
                        {"name" : "age", "value" : 15, "prompt" : "User age"},
                        {"name" : "gender", "value" : 1, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/6/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/6/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/6/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/6/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/6/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/6/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/6/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/6/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "email", "value" : "", "prompt" : "User email", "required" : "true"},
                    {"name" : "password", "value" : "", "prompt" : "User password", "required" : "true"},
                    {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "true"},
                    {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                    {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "true"},
                    {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                    {"name" : "age", "value" : "", "prompt" : "User age", "required" : "true"},
                    {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "true"}
                ]
            },
            "queries" : [
                {
                    "href" : "/friendsNet/api/users/",
                    "rel" : "search",
                    "prompt" : "Search user",
                    "data" : [
                        {"name" : "name", "value" : ""},
                        {"name" : "surname", "value" : ""}
                    ]
                }
            ]
        }
    }

    resp_get_surname_query = {
        "collection" : {
            "version" : "1.0",
            "href" : "/friendsNet/api/users/",
            "items" : [
                {
                    "href" : "/friendsNet/api/users/1/profile/",
                    "data" : [
                        {"name" : "id", "value" : 1, "prompt" : "User id"},
                        {"name" : "firstName", "value" : "Antonio", "prompt" : "User first name"},
                        {"name" : "surname", "value" : "Antonino", "prompt" : "User surname"},
                        {"name" : "age", "value" : 20, "prompt" : "User age"},
                        {"name" : "gender", "value" : 0, "prompt" : "User gender"}
                    ],
                    "links" : [
                        {"href" : "/friendsNet/api/users/1/groups/", "rel" : "user memberships", "prompt" : "User memberships"},
                        {"href" : "/friendsNet/api/users/1/comments/", "rel" : "user comments", "prompt" : "User comments"},
                        {"href" : "/friendsNet/api/users/1/rates/", "rel" : "user rates", "prompt" : "User rates"},
                        {"href" : "/friendsNet/api/users/1/tags/", "rel" : "user tags", "prompt" : "User tags"},
                        {"href" : "/friendsNet/api/users/1/statuses/", "rel" : "user statuses", "prompt" : "User statuses"},
                        {"href" : "/friendsNet/api/users/1/friendships/", "rel" : "user friendships", "prompt" : "User friendships"},
                        {"href" : "/friendsNet/api/users/1/conversations/", "rel" : "user conversations", "prompt" : "User conversations"},
                        {"href" : "/friendsNet/api/users/1/feed/", "rel" : "user feed", "prompt" : "User feed"}
                    ]
                }
            ],
            "template" : {
                "data" : [
                    {"name" : "email", "value" : "", "prompt" : "User email", "required" : "true"},
                    {"name" : "password", "value" : "", "prompt" : "User password", "required" : "true"},
                    {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "true"},
                    {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                    {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "true"},
                    {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                    {"name" : "age", "value" : "", "prompt" : "User age", "required" : "true"},
                    {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "true"}
                ]
            },
            "queries" : [
                {
                    "href" : "/friendsNet/api/users/",
                    "rel" : "search",
                    "prompt" : "Search user",
                    "data" : [
                        {"name" : "name", "value" : ""},
                        {"name" : "surname", "value" : ""}
                    ]
                }
            ]
        }
    }

    profile_post_correct = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "emailnew"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "middle_name", "value" : "John"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 3},
                {"name" : "age", "value" : 13},
                {"name" : "gender", "value" : 0}
            ]
        }
    }

    profile_post_prof_picture_id_wrong = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "emailnew"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 999},
                {"name" : "age", "value" : 13},
                {"name" : "gender", "value" : 0}
            ]
        }
    }

    profile_post_age_wrong = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "emailnew"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 999},
                {"name" : "age", "value" : -2},
                {"name" : "gender", "value" : 0}
            ]
        }
    }

    profile_post_gender_wrong = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "emailnew"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 2},
                {"name" : "age", "value" : 18},
                {"name" : "gender", "value" : 6}
            ]
        }
    }

    profile_post_incorrect = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "emailnew"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : "err"},
                {"name" : "age", "value" : 18},
                {"name" : "gender", "value" : 2}
            ]
        }
    }

    profile_post_email_existing = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "email1@gmail.com"},
                {"name" : "password", "value" : "correctPW"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 2},
                {"name" : "age", "value" : 18},
                {"name" : "gender", "value" : 2}
            ]
        }
    }

    profile_post_password_incorrect = {
        "template" : {
            "data" : [
                {"name" : "email", "value" : "newEmail"},
                {"name" : "password", "value" : "short"},
                {"name" : "firstName", "value" : "Jack"},
                {"name" : "surname", "value" : "Sparrow"},
                {"name" : "prof_picture_id", "value" : 2},
                {"name" : "age", "value" : 18},
                {"name" : "gender", "value" : 2}
            ]
        }
    }

    def setUp(self):
        super(UserProfilesTestCase , self).setUp()
        self.url = resources.api.url_for(resources.User_profiles, _external = False)
        self.url_name = resources.api.url_for(resources.User_profiles, name = "Trial", _external = False)
        self.url_surname = resources.api.url_for(resources.User_profiles, surname = "Antonino", _external = False)

#TEST URL
    def test_url(self):
        #Checks that the URL points to the right resource
        _url = '/friendsNet/api/users/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User_profiles)

#TEST GET
#200 + MIMETYPE & PROFILE
    def test_get_profiles(self):
        print '('+self.test_get_profiles.__name__+')', self.test_get_profiles.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + USER_PROFILE)

#SEARCH BY NAME
    def test_get_profiles_name(self):
        print '('+self.test_get_profiles_name.__name__+')', self.test_get_profiles_name.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_name, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_name_query, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + USER_PROFILE)

#SEARCH BY SURNAME
    def test_get_profiles_surname(self):
        print '('+self.test_get_profiles_surname.__name__+')', self.test_get_profiles_surname.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url_surname, headers = {"Accept" : COLLECTION_JSON})
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            self.assertEquals(self.resp_get_surname_query, data)
            self.assertEqual(resp.headers.get("Content-Type", None), COLLECTION_JSON + ";profile=" + USER_PROFILE)

#TEST POST
#201
    def test_post_profile(self):
        print '('+self.test_post_profile.__name__+')', self.test_post_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_correct), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 201)

        self.assertIn("Location", resp.headers)
        new_url = resp.headers["Location"]
        resp2 = self.client.get(new_url, headers = {"Accept" : HAL_JSON})
        self.assertEquals(resp2.status_code, 200)

#400 wrong format
    def test_post_incorrect_profile(self):
        print '('+self.test_post_incorrect_profile.__name__+')', self.test_post_incorrect_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_incorrect), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 incorrect password
    def test_post_incorrect_password_profile(self):
        print '('+self.test_post_incorrect_password_profile.__name__+')', self.test_post_incorrect_password_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_password_incorrect), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 incorrect age
    def test_post_incorrect_age_profile(self):
        print '('+self.test_post_incorrect_age_profile.__name__+')', self.test_post_incorrect_age_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_age_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#400 incorrect gender
    def test_post_incorrect_gender_profile(self):
        print '('+self.test_post_incorrect_gender_profile.__name__+')', self.test_post_incorrect_gender_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_gender_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 400)

#404 profile picture not existing
    def test_post_not_existing_picture_profile(self):
        print '('+self.test_post_not_existing_picture_profile.__name__+')', self.test_post_not_existing_picture_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_prof_picture_id_wrong), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 404)

#409
    def test_post_existing_email_profile(self):
        print '('+self.test_post_existing_email_profile.__name__+')', self.test_post_existing_email_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_email_existing), headers = {"Content-Type" : COLLECTION_JSON})
        self.assertEquals(resp.status_code, 409)

#415
    def test_post_wrong_header_profile(self):
        print '('+self.test_post_wrong_header_profile.__name__+')', self.test_post_wrong_header_profile.__doc__
        resp = self.client.post(self.url, data = json.dumps(self.profile_post_correct))
        self.assertEquals(resp.status_code, 415)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
