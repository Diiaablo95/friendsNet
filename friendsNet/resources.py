import json

from flask import Flask, request, Response, g, jsonify, _request_ctx_stack, redirect, send_from_directory
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature)
from flask.ext.restful import Resource, Api
from werkzeug.utils import secure_filename
import os

import database

################################################### CONSTANTS ###################################################

COLLECTION_JSON = "application/vnd.collection+json"
HAL_JSON = "application/hal+json"
MULTI_PART = "multipart/form-data"
JSON = "application/json"

API_VERSION = "1.0"

USER_PROFILE = "/profiles/user-profile"
MEDIA_ITEM_PROFILE = "/profiles/media_item-profile"
COMMENT_PROFILE = "/profiles/comment-profile"
RATE_PROFILE = "/profiles/rate-profile"
CONVERSATION_PROFILE = "/profiles/conversation-profile"
FRIENDSHIP_PROFILE = "/profiles/friendship-profile"
MESSAGE_PROFILE = "/profiles/message-profile"
STATUS_PROFILE = "/profiles/status-profile"
GROUP_PROFILE = "/profiles/group-profile"
GROUP_MEMBERSHIP_REQUEST_PROFILE = "/profiles/request-profile"
GROUP_MEMBERSHIP_PROFILE = "/profiles/membership-profile"

APIARY_PROFILES_URL = "http://docs.friendsnetapis.apiary.io/#reference/profiles"

MEDIA_SAVING_FOLDER = "media_uploads/"
ALLOWED_EXTENSIONS = {"jpg", "mp4"}
ALLOWED_RETURNED_TYPES = {"jpg" : "image/jpg", "mp4" : "video/mp4"}

MULTIPART_FILE_KEY = "new media item"
################################################### SETTINGS ###################################################

#Define the application and the api
app = Flask(__name__, static_folder = MEDIA_SAVING_FOLDER, static_url_path = "/friendsNet/")
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path app.config to modify the
#database to be used (for instance for testing)
app.config.update({"Engine": database.Engine()})

#Set allowed extensions for uploaded media
app.config.update({"ALLOWED_EXTENSIONS" : ALLOWED_EXTENSIONS})

#Set secret key to generate tokens
app.config.update({"SECRET_KEY" : "?mIsunderSt@ndings!"})

app.config.update({"LAST_MEDIA_ITEM_ID" : -1})
#Start the RESTful API.
api = Api(app)

#Redirect profile
@app.route('/profiles/<profile_name>/')
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL)

################################################### ERRORS DEFINITION ###################################################

def create_error_response(status_code, title, message, resp_type = COLLECTION_JSON):
    '''
    Always returns errors following collection hypermedia format
    '''
    resp = None
    href = None
    ctx = _request_ctx_stack.top
    if ctx is not None:
        href = request.path
    if href is not None:
        if resp_type == COLLECTION_JSON:
            href = None
            ctx = _request_ctx_stack.top
            if ctx is not None:
                href = request.path
            resp = {
                "collection" : {
                    "version" : "1.0",
                    "href" : href,
                    "error" : {"code" : status_code, "title" : title, "message" : message}
                }
            }
            resp = jsonify(resp)
            resp.status_code = status_code
            resp.content_type = COLLECTION_JSON
        elif resp_type == HAL_JSON:
            resp = {"code" : status_code,
                    "title" : title,
                    "message" : message,
                    "resource_url" : href
                    }
            resp = jsonify(resp)
            resp.status_code = status_code
            resp.content_type = HAL_JSON
    return resp

def bad_request(parameter_name = "Parameter"):
    return create_error_response(status_code = 400, title = parameter_name + " in bad format.", message = parameter_name + " passed in a bad format for the request. Please check documentation.")

def unauthenticated_user(parameter_name):
    return create_error_response(status_code = 401, title = "Wrong " + parameter_name + ".", message = "Wrong " + parameter_name + " passed.", resp_type = HAL_JSON)

def unauthorized_action(title = "Impossible to satisfy the request.", message = "Some preconditions for request to be satisfied are missing. Please check documentation."):
    return create_error_response(status_code = 403, title = title, message = message)

def resource_not_found(parameter_name = "Parameter", resp_type = COLLECTION_JSON):
    return create_error_response(status_code = 404, title = parameter_name + " not found.", message = parameter_name + " not present in the system.", resp_type = resp_type)

def double_resource_attribute(parameter_name = "Resource"):
    return create_error_response(status_code = 409, title = parameter_name + " double.", message = parameter_name + " already present in the system.")

def unsupported_media_type():
    ERROR_415 = {"code" : 415, "title" : "Error in request body format.", "message" : "Server cannot understand format of request body."}
    return create_error_response(status_code = ERROR_415["code"], title = ERROR_415["title"], message = ERROR_415["message"])

def internal_server_error():
    ERROR_500 = {"code" : 500, "title" : "Error in saving data.", "message" : "Server cannot store resource in the database."}
    return create_error_response(status_code = ERROR_500["code"], title = ERROR_500["title"], message = ERROR_500["message"])

################################################### UTILITY METHODS ###################################################

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in app.config["ALLOWED_EXTENSIONS"]

# Return the type of the file, if one of the available one, otherwise it returns None
def get_file_extension(filename):
    extension = None

    if allowed_file(filename):
        parts = filename.split(".")
        extension = parts[len(parts) - 1]   #Only part after last "."

    return extension

def get_file_type(file_extension):
    file_type = -1
    if file_extension.lower() == "jpg":
        file_type = 0
    elif file_extension.lower() == "mp4":
        file_type = 1

    return file_type

def get_file_mimetype(file_extension):
    return ALLOWED_RETURNED_TYPES.get(file_extension, None)

def get_file_name(url):
    parts = url.split("/")
    name = parts[len(parts) - 1]
    return name

################################################### SETUP/TEARDOWN REQUEST DEFINITION ###################################################

@app.before_request
def connect_db():
    '''Creates a database connection before the request is proccessed.

        The connection is stored in the application context variable flask.g .
        Hence it is accessible from the request object.'''

    g.con = app.config["Engine"].connect()

    if app.config["LAST_MEDIA_ITEM_ID"] == -1:              #Since it's not possible to catch event in which the app is launched, before every request
        last_id = g.con.get_last_media_item_id()            #the system checks that the value for naming the new images has been updated
        app.config["LAST_MEDIA_ITEM_ID"] = last_id

@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It migth be exception appear before
        the connection is created.'''
    if hasattr(g, "con"):
        g.con.close()

#METHOD UTILIZED FOR GET IS ALWAYS THE SAME: BUILD THE RESPONSE OBJECT BASED ON THE DOCUMENTATION WRITTEN (commented, informally, just first get method).
#FOR POST AND PUT METHOD, IT'S SLIGHTLY DIFFERENT SINCE FOR BOTH SOME CHECKS HAVE TO BE MADE.
#DELETE METHOD IS THE SIMPLEST ONE SINCE IT JUST CHECKS THE RETURN VALUE FROM DATABASE TO RETURN RESPONSE TO USER.

def generate_auth_token(user_id):
    s = Serializer(app.config["SECRET_KEY"], expires_in = 99999999999999999999999999999)
    return s.dumps({"id" : user_id})

def verify_auth_token(token):
    authenticated_user_id = None

    s = Serializer(app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
        authenticated_user_id = data["id"]
    except BadSignature:
        pass
    return authenticated_user_id

################################################### USER METHODS DEFINITION ###################################################

##################### USER COMMENTS #####################

class User_comments(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:                     #If user is not in the db then error
            resp = resource_not_found(parameter_name = "User")
        else:
            user_comments = g.con.get_comments_for_user(user_id)            #Get all comments from db

            items = []

            if user_comments is not None:
                for comment in user_comments:                                   #If no comments, then empty array is returned
                    comment_id = comment["comment_id"]
                    status_id = comment["status_id"]
                    content = comment["content"]
                    creation_time = comment["creation_time"]

                    item = {}

                    item["href"] = api.url_for(Comment, comment_id = comment_id)

                    item["data"] = [{"name" : "id", "value" : comment_id, "prompt" : "Comment id"},
                                    {"name" : "status_id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "content", "value" : content, "prompt" : "Content"},
                                    {"name" : "creation_time", "value" : creation_time, "prompt" : "Creation time"}]

                    item["links"] = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status commented"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "author", "prompt" : "User profile"}]

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_comments, user_id = user_id),
                "links" : links,
                "items" : items
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + COMMENT_PROFILE)
        return resp

##################### USER RATES #####################

class User_rates(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:                 #If no user in db, then error
            resp = resource_not_found(parameter_name = "User")
        else:
            user_rates = g.con.get_rates_for_user(user_id)

            items = []                                                  #If no rates for the user, than empty array is returned

            if user_rates is not None:
                for rate in user_rates:
                    rate_id = rate["rate_id"]
                    status_id = rate["status_id"]
                    rate = rate["rate"]

                    item = {}

                    item["href"] = api.url_for(Rate, rate_id = rate_id)

                    item["data"] = [{"name" : "id", "value" : rate_id, "prompt" : "Rate id"},
                                    {"name" : "status_id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "rate", "value" : rate, "prompt" : "Rate value"}]

                    item["links"] = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status rated"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "author", "prompt" : "User profile"}]

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_rates, user_id = user_id),
                "links" : links,
                "items" : items
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + RATE_PROFILE)
        return resp

##################### USER CONVERSATIONS #####################

class User_conversations(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:             #If no user in db, then error
            resp = resource_not_found(parameter_name = "User")
        else:
            user_conversations = g.con.get_conversations_for_user(user_id)

            items = []

            if user_conversations is not None:
                for conversation in user_conversations:                 #If no conversation for the user, then empty array is returned
                    conversation_id = conversation["conversation_id"]
                    user1_id = conversation["user1_id"]
                    user2_id = conversation["user2_id"]
                    time_last_message = conversation["time_last_message"]

                    item = {}

                    item["href"] = api.url_for(Conversation, conversation_id = conversation_id)

                    item["data"] = [{"name" : "id", "value" : conversation_id, "prompt" : "Conversation id"},
                                    {"name" : "user1_id", "value" : user1_id, "prompt" : "User_1 id"},
                                    {"name" : "user2_id", "value" : user2_id, "prompt" : "User_2 id"},
                                    {"name" : "time_last_message", "value" : time_last_message, "prompt" : "Time last message"}]

                    item["links"] = [{"href" : api.url_for(User_profile, user_id = user2_id), "rel" : "user contacted profile", "prompt" : "User contacted profile"},
                                     {"href" : api.url_for(Conversation_messages, conversation_id = conversation_id), "rel" : "conversation messages", "prompt" : "Conversation messages"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "user profile", "prompt" : "User profile"}]

            template = {"data" : [{"name" : "user2_id", "value" : "", "prompt" : "User_2 id", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_conversations, user_id = user_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + CONVERSATION_PROFILE)
        return resp

    def post(self, user_id):
        resp = None

        USER_2_ID = "user2_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_user_information(user_id) is None:                 #If no user in db, then error
            resp = resource_not_found(parameter_name = "User")
        else:
            try:
                request_body = request.get_json(force = True)                           #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                        #Get data element of template
                #for every dictionary in the array, filters the one (if it is) with value of key "name" equal to "user_2_id" and takes the value of the key "value"
                #Then, the returned array will have just one element which corresponds to the string value of the variable.
                values_array = list(data["value"] for data in template_data if data["name"] == USER_2_ID)
                user2_id = int(values_array[0])

                if g.con.get_user_information(user2_id) is None:
                    resp = resource_not_found(parameter_name = "User")
                else:
                    conversations = g.con.get_conversations_for_user(user_id)
                    filtered_conversations_list = list(conversation for conversation in conversations if conversation["user1_id"] == user2_id or conversation["user2_id"] == user2_id) if conversations is not None else []
                    if len(filtered_conversations_list) > 0:
                        resp = double_resource_attribute(parameter_name = "User email")
                    else:
                        new_conversation = {"user1_id" : user_id, "user2_id" : user2_id}    #Create conversation in database
                        new_conversation_id = g.con.create_conversation(new_conversation)

                        if new_conversation_id is None:                     #If impossible to create new conversation, then error
                            resp = internal_server_error()
                        else:
                            new_url = api.url_for(Conversation, conversation_id = new_conversation_id)
                            resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "User id")                            #If anything wrong (due to bad request format), then error
        return resp

##################### USER AUTHENTICATION #####################

class User_authentication(Resource):

    def post(self):
        resp = None
        if request.headers.get("Content-Type", "") != JSON:
            resp = unsupported_media_type()
        else:
            request_body = request.get_json(force = True)

            email = request_body.get("email", "")
            if email == "":         #If user sends an authorization token
                token = request_body.get("token", "")
                user_id = verify_auth_token(token)

                if user_id is None:                             #If token doesn't exist
                    resp = unauthenticated_user(parameter_name = "authorization token")
                else:
                    result = {"user_id" : user_id, "auth_token" : token}
                    resp = Response(json.dumps(result), 201, mimetype = JSON)
            else:                                               #If user sends email (and password)
                password = request_body.get("password", "")

                found_user_id = g.con.get_user_id(email, password)

                if found_user_id is None:
                    resp = unauthenticated_user(parameter_name = "email/password combination")
                else:
                    generated_token = generate_auth_token(found_user_id)
                    result = {"user_id" : found_user_id, "auth_token" : generated_token}
                    resp = Response(json.dumps(result), 201, mimetype = JSON)
        return resp

##################### USER FRIENDSHIPS #####################

class User_friendships(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:                 #If user not in db, then error
            resp = resource_not_found(parameter_name = "User")
        else:
            user_friendships = g.con.get_friendships_for_user(user_id)

            items = []

            if user_friendships is not None:
                for friendship in user_friendships:                       #If no friendship, then empty array is returned
                    friendship_id = friendship["friendship_id"]
                    user1_id = friendship["user1_id"]
                    user2_id = friendship["user2_id"]
                    status = friendship["friendship_status"]
                    start = friendship["friendship_start"]

                    item = {}

                    item["href"] = api.url_for(Friendship, friendship_id = friendship_id)

                    item["data"] = [{"name" : "id", "value" : friendship_id, "prompt" : "Friendship id"},
                                    {"name" : "user1_id", "value" : user1_id, "prompt" : "User_1 id"},
                                    {"name" : "user2_id", "value" : user2_id, "prompt" : "User_2 id"},
                                    {"name" : "friendship_status", "value" : status, "prompt" : "Friendship status"},
                                    {"name" : "friendship_start", "value" : start, "prompt" : "Friendship start"}]

                    item["links"] = [{"href" : api.url_for(User_profile, user_id = user2_id), "rel" : "friend", "prompt" : "Friend profile"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "user profile", "prompt" : "User profile"}]

            template = {"data" : [{"name" : "user2_id", "value" : "", "prompt" : "User_2 id", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_friendships, user_id = user_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + FRIENDSHIP_PROFILE)
        return resp

    def post(self, user_id):
        resp = None

        USER_2_ID = "user2_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_user_information(user_id) is None:                                 #If user not in db, then error
            resp = resource_not_found(parameter_name = "User")
        else:
            try:
                request_body = request.get_json(force = True)                           #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                        #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == USER_2_ID)
                user2_id = int(values_array[0])     #INT USED ON PURPOSE TO GENERATE EXCEPTION IS FORMAT IS WRONG

                if g.con.get_user_information(user2_id) is None:
                    resp = resource_not_found(parameter_name = "User")
                else:
                    friendships = g.con.get_friendships_for_user(user_id)
                    filtered_friendships_list = list(friendship for friendship in friendships if friendship["user1_id"] == user2_id or friendship["user2_id"] == user2_id) if friendships is not None else []
                    if len(filtered_friendships_list) > 0:
                        resp = double_resource_attribute(parameter_name = "Friendship")
                    else:
                        new_friendship_id = g.con.create_friendship(user_id, user2_id)

                        if new_friendship_id is None:
                            resp = internal_server_error()
                        else:
                            new_url = api.url_for(Friendship, friendship_id = new_friendship_id)
                            resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "User id")
        return resp

##################### USER MEMBERSHIPS #####################

class User_memberships(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            user_memberships = g.con.get_groups_for_user(user_id)

            items = []

            if user_memberships is not None:
                for membership in user_memberships:
                    group_id = membership["group_id"]
                    user_type = membership["administrator"]

                    item = {}

                    item["href"] = api.url_for(User_membership, user_id = user_id, group_id = group_id)

                    item["data"] = [{"name" : "id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "group_id", "value" : group_id, "prompt" : "Group id"},
                                    {"name" : "administrator", "value" : user_type, "prompt" : "Membership type"}]

                    item["links"] = [{"href" : api.url_for(Group, group_id = group_id), "rel" : "group", "prompt" : "Group"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "user profile", "prompt" : "User profile"}]

            template = {"data" : [{"name" : "group_id", "value" : "", "prompt" : "Group id", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_memberships, user_id = user_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_PROFILE)
        return resp

    def post(self, user_id):
        resp = None

        GROUP_ID = "group_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == GROUP_ID)
                group_id = int(values_array[0])

                if g.con.get_information_for_group(group_id) is None:
                    resp = resource_not_found(parameter_name = "Group")
                else:
                    memberships = g.con.get_groups_for_user(user_id)
                    filtered_memberships_list = list(membership for membership in memberships if membership["group_id"] == group_id) if memberships is not None else []
                    if len(filtered_memberships_list) > 0:
                        resp = double_resource_attribute(parameter_name = "Membership")
                    else:
                        if not g.con.add_member_to_group(group_id, user_id):
                            resp = internal_server_error()
                        else:
                            new_url = api.url_for(User_membership, user_id = user_id, group_id = group_id)
                            resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "Group id")
        return resp

##################### USER MEMBERSHIP #####################

class User_membership(Resource):

    def get(self, user_id, group_id):
        resp = None

        if ((g.con.get_user_information(user_id) is None) or (g.con.get_information_for_group(group_id) is None)):  #If either group or user doesn't exist, then error
            resp = resource_not_found(parameter_name = "User", resp_type = HAL_JSON)
        else:
            memberships = g.con.get_groups_for_user(user_id)
            filtered_user_memberships = list(group for group in memberships if group["group_id"] == group_id) if memberships is not None else [] #either 0 or 1 element in the array
            user_membership = filtered_user_memberships[0] if len(filtered_user_memberships) > 0 else None

            if user_membership is not None:
                user_id = user_membership["user_id"]
                group_id = user_membership["group_id"]
                administrator = user_membership["administrator"]

                _links = {"self" : {"href" : api.url_for(User_membership, user_id = user_id, group_id = group_id), "profile" : GROUP_MEMBERSHIP_PROFILE},
                         "group members" : {"href" : api.url_for(Group_members, group_id = group_id)},
                         "user memberships" : {"href" : api.url_for(User_memberships, user_id = user_id)},
                         "user profile" : {"href" : api.url_for(User_profile, user_id = user_id)}
                }

                template = {
                    "data" : [
                        {"name" : "administrator", "value" : "", "prompt" : "Membership type", "required" : "false"}
                    ]
                }

                hal = {
                    "user_id" : user_id,
                    "group_id" : group_id,
                    "administrator" : administrator,
                    "_links" : _links,
                    "template" : template
                }

                resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
            else:
                resp = resource_not_found(parameter_name = "Membership", resp_type = HAL_JSON)

        return resp

    def patch(self, user_id, group_id):
        resp = None
        server_error = False

        ADMINISTRATOR = "administrator"

        memberships = g.con.get_groups_for_user(user_id)
        filtered_user_memberships = list(group for group in memberships if group["group_id"] == group_id) if memberships is not None else []
        user_membership = filtered_user_memberships[0] if len(filtered_user_memberships) > 0 else None

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif user_membership is None:
            resp = resource_not_found(parameter_name = "Membership")                 #If membership is not in db, then error
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == ADMINISTRATOR)
                administrator = int(values_array[0]) if len(values_array) > 0 else None

                if administrator is not None:
                    if administrator == 1 or administrator == 0:
                        new_membership = {"user_id": user_id, "administrator": administrator}
                        if not g.con.update_group_member(group_id, new_membership):
                            resp = internal_server_error()
                            server_error = True
                    elif administrator != 0 and administrator != 1:
                        resp = bad_request(parameter_name = "Membership type value")
                        server_error = True

                if not server_error:
                    resp = Response(status = 204)  # Since administrator is not required, then request is completed either the value is passed or not
            except:
                resp = bad_request(parameter_name = "Membership type")
        return resp

    def delete(self, user_id, group_id):
        resp = None

        if g.con.delete_member(group_id, user_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Membership")
        return resp

##################### USER TAGS #####################
class User_tags(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            user_tags = g.con.get_tagged_statuses_for_user(user_id)

            items = []

            if user_tags is not None:
                for status in user_tags:
                    status_id = status["status_id"]
                    creator_id = status["creator_id"]
                    content = status["content"]
                    creation_time = status["creation_time"]

                    item = {}

                    item["href"] = api.url_for(Status, status_id = status_id)

                    item["data"] = [{"name" : "id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : creator_id, "prompt" : "Creator id"},
                                    {"name" : "content", "value" : content, "prompt" : "Status content"},
                                    {"name" : "creation_time", "value" : creation_time, "prompt" : "Status creation time"}]

                    item["links"] = [{"href" : api.url_for(Status_comments, status_id = status_id), "rel" : "status comments", "prompt" : "Status comments"},
                                     {"href" : api.url_for(Status_rates, status_id = status_id), "rel" : "status rates", "prompt" : "Status rates"},
                                     {"href" : api.url_for(Status_tags, status_id = status_id), "rel" : "status tags", "prompt" : "Status tags"},
                                     {"href" : api.url_for(Status_media, status_id = status_id), "rel" : "media list", "prompt" : "Status media items"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "tag", "prompt" : "User profile"}]

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_tags, user_id = user_id),
                "links" : links,
                "items" : items
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + STATUS_PROFILE)
        return resp

##################### USER PROFILES #####################

class User_profiles(Resource):

    def get(self):
        resp = None

        name = request.args.get("name", "")
        surname = request.args.get("surname", "")
        user_profiles = g.con.search_user(name, surname)

        items = []

        if user_profiles is not None:
            for user_profile in user_profiles:
                user_id = user_profile["user_id"]
                first_name = user_profile["first_name"]
                middle_name = user_profile["middle_name"]
                surname = user_profile["surname"]
                prof_picture_id = user_profile["prof_picture_id"]
                age = user_profile["age"]
                gender = user_profile["gender"]

                item = {}

                item["href"] = api.url_for(User_profile, user_id=user_id)

                item["data"] = [{"name": "id", "value": user_id, "prompt": "User id"},
                                {"name": "firstName", "value": first_name, "prompt": "User first name"}]

                if middle_name is not None:
                    item["data"].append({"name" : "middle_name", "value" : middle_name, "prompt" : "User middle name"})

                item["data"].extend([
                    {"name": "surname", "value": surname, "prompt": "User surname"},
                    {"name": "age", "value": age, "prompt": "User age"},
                    {"name": "gender", "value": gender, "prompt": "User gender"}
                ])

                if prof_picture_id is not None:
                    item["data"].append({"prof_picture_id": prof_picture_id})

                item["links"] = [{"href": api.url_for(User_memberships, user_id = user_id), "rel": "user memberships", "prompt": "User memberships"},
                                 {"href": api.url_for(User_comments, user_id = user_id), "rel": "user comments", "prompt": "User comments"},
                                 {"href": api.url_for(User_rates, user_id = user_id), "rel": "user rates", "prompt": "User rates"},
                                 {"href": api.url_for(User_tags, user_id = user_id), "rel": "user tags", "prompt": "User tags"},
                                 {"href": api.url_for(User_statuses, user_id = user_id), "rel": "user statuses", "prompt": "User statuses"},
                                 {"href": api.url_for(User_friendships, user_id = user_id), "rel": "user friendships", "prompt": "User friendships"},
                                 {"href": api.url_for(User_conversations, user_id = user_id), "rel": "user conversations", "prompt": "User conversations"},
                                 {"href": api.url_for(User_feed, user_id = user_id), "rel": "user feed", "prompt": "User feed"}]

                if prof_picture_id is not None:
                    item["links"].append({"href" : api.url_for(Media_item, media_id = prof_picture_id), "rel" : "profile picture", "prompt" : "User profile picture"})

                items.append(item)

        template = {"data": [{"name": "email", "value": "", "prompt": "User email", "required": "true"},
                             {"name": "password", "value": "", "prompt": "User password", "required": "true"},
                             {"name": "firstName", "value": "", "prompt": "User first name", "required": "true"},
                             {"name": "middle_name", "value": "", "prompt": "User middle name", "required": "false"},
                             {"name": "surname", "value": "", "prompt": "User surname", "required": "true"},
                             {"name": "prof_picture_id", "value": "", "prompt": "Profile picture id", "required": "false"},
                             {"name": "age", "value": "", "prompt": "User age", "required": "true"},
                             {"name": "gender", "value": "", "prompt": "User gender", "required": "true"}]}

        queries = [{"href": api.url_for(User_profiles),
                    "rel": "search",
                    "prompt": "Search user",
                    "data": [{"name": "name", "value": ""},
                             {"name": "surname", "value": ""}]}]

        collection = {
            "version": API_VERSION,
            "href": api.url_for(User_profiles),
            "items": items,
            "template": template,
            "queries": queries
        }

        envelope = {"collection": collection}

        resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + USER_PROFILE)
        return resp

    def post(self):
        resp = None

        EMAIL = "email"
        PASSWORD = "password"
        FIRST_NAME = "firstName"
        MIDDLE_NAME = "middle_name"
        SURNAME = "surname"
        PROF_PICTURE_ID = "prof_picture_id"
        AGE = "age"
        GENDER = "gender"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        else:
            try:
                a = request
                request_body = request.get_json(force = True)                           #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                        #Get data element of template

                email = list(data["value"] for data in template_data if data["name"] == EMAIL)[0]
                password = list(data["value"] for data in template_data if data["name"] == PASSWORD)[0]
                first_name = list(data["value"] for data in template_data if data["name"] == FIRST_NAME)[0]
                middle_name_value_array = list(data["value"] for data in template_data if data["name"] == MIDDLE_NAME)
                middle_name = middle_name_value_array[0] if len(middle_name_value_array) > 0 else None
                surname = list(data["value"] for data in template_data if data["name"] == SURNAME)[0]
                prof_picture_value_array = list(data["value"] for data in template_data if data["name"] == PROF_PICTURE_ID)
                prof_picture_id = int(prof_picture_value_array[0]) if len(prof_picture_value_array) > 0 else None
                age = int(list(data["value"] for data in template_data if data["name"] == AGE)[0])
                gender = int(list(data["value"] for data in template_data if data["name"] == GENDER)[0])

                if g.con.is_email_existing(email):
                    resp = double_resource_attribute(parameter_name = "User email")
                else:
                    if age < 0:
                        resp = bad_request(parameter_name = "User age value")
                    elif gender < 0 or gender > 2:
                        resp = bad_request(parameter_name = "User gender value")
                    elif len(password) < 8:
                        resp = bad_request(parameter_name = "Password value")
                    else:
                        new_user = {"email" : email, "password" : password, "first_name" : first_name, "surname" : surname, "age" : age, "gender" : gender}

                        if middle_name is not None:
                            new_user["middle_name"] = middle_name
                        if prof_picture_id is not None:
                            if g.con.get_media_item(prof_picture_id) is None:
                                resp = resource_not_found(parameter_name = "Media item")
                            else:
                                new_user["prof_picture_id"] = prof_picture_id

                        new_user_id = g.con.create_user(new_user)
                        if new_user_id is None:
                            resp = internal_server_error()
                        else:
                            new_url = api.url_for(User_profile, user_id = new_user_id)
                            resp = Response(status = 201, headers = {"Location" : new_url})
            except Exception, e:
                resp = bad_request(parameter_name = "Profile picture id, user age or user gender")
        return resp

##################### USER PROFILE #####################

class User_profile(Resource):

    def get(self, user_id):
        resp = None

        user_profile = g.con.get_user_information(user_id)

        if user_profile is None:
            resp = resource_not_found(parameter_name = "User", resp_type = HAL_JSON)
        else:
            first_name = user_profile["first_name"]
            middle_name = user_profile["middle_name"]
            surname = user_profile["surname"]
            prof_picture_id = user_profile["prof_picture_id"]
            age = user_profile["age"]
            gender = user_profile["gender"]

            _links = {"self" : {"href" : api.url_for(User_profile, user_id = user_id), "profile" : USER_PROFILE},
                      "user memberships" : {"href" : api.url_for(User_memberships, user_id = user_id)},
                      "user comments" : {"href" : api.url_for(User_comments, user_id = user_id)},
                      "user rates" : {"href" : api.url_for(User_rates, user_id = user_id)},
                      "user tags" : {"href" : api.url_for(User_tags, user_id = user_id)},
                      "user statuses" : {"href" : api.url_for(User_statuses, user_id = user_id)},
                      "user friendships" : {"href" : api.url_for(User_friendships, user_id = user_id)},
                      "user conversations" : {"href" : api.url_for(User_conversations, user_id = user_id)},
                      "user feed" : {"href" : api.url_for(User_feed, user_id = user_id)}}

            template = {"data" : [{"name" : "password", "value" : "", "prompt" : "User password", "required" : "false"},
                                  {"name" : "firstName", "value" : "", "prompt" : "User first name", "required" : "false"},
                                  {"name" : "middle_name", "value" : "", "prompt" : "User middle name", "required" : "false"},
                                  {"name" : "surname", "value" : "", "prompt" : "User surname", "required" : "false"},
                                  {"name" : "prof_picture_id", "value" : "", "prompt" : "Profile picture id", "required" : "false"},
                                  {"name" : "age", "value" : "", "prompt" : "User age", "required" : "false"},
                                  {"name" : "gender", "value" : "", "prompt" : "User gender", "required" : "false"}]}

            hal = {
                "id" : user_id,
                "firstName" : first_name,
                "surname" : surname,
                "age" : age,
                "gender" : gender,
                "_links" : _links,
                "template" : template
            }

            if middle_name is not None:
                hal["middle_name"] = middle_name
            if prof_picture_id is not None:
                hal["prof_picture_id"] = prof_picture_id

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp


    def patch(self, user_id):
        resp = None
        server_error = False

        PASSWORD = "password"
        FIRST_NAME = "firstName"
        MIDDLE_NAME = "middle_name"
        SURNAME = "surname"
        PROF_PICTURE_ID = "prof_picture_id"
        AGE = "age"
        GENDER = "gender"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == PASSWORD)
                password = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == FIRST_NAME)
                first_name = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == MIDDLE_NAME)
                middle_name = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == SURNAME)
                surname = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == PROF_PICTURE_ID)
                prof_picture_id = int(values_array[0]) if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == AGE)
                age = int(values_array[0]) if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == GENDER)
                gender = int(values_array[0]) if len(values_array) > 0 else None

                new_user = {}
                if password is not None:
                    if len(password) < 8:
                        resp = bad_request(parameter_name = "Password value")
                        server_error = True
                    else:
                        new_user["password"] = password
                if first_name is not None:
                    new_user["first_name"] = first_name
                if middle_name is not None:
                    new_user["middle_name"] = middle_name
                if surname is not None:
                    new_user["surname"] = surname
                if prof_picture_id is not None:
                    if g.con.get_media_item(prof_picture_id) is not None:
                        new_user["prof_picture_id"] = prof_picture_id
                    else:
                        resp = resource_not_found(parameter_name = "Media item")
                        server_error = True
                if age is not None:
                    if age < 0:
                        resp = bad_request(parameter_name = "User age value")
                        server_error = True
                    else:
                        new_user["age"] = age
                if gender is not None:
                    if gender < 0 or gender > 2:
                        resp = bad_request(parameter_name = "User gender value")
                        server_error = True
                    else:
                        new_user["gender"] = gender

                if not g.con.update_user(user_id, new_user):
                    resp = internal_server_error()
                    server_error = True

                if not server_error:
                    resp = Response(status = 204)
            except:
                resp = bad_request(parameter_name = "Profile picture id, user age or user gender")
        return resp

    def delete(self, user_id):
        resp = None

        if g.con.delete_user(user_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "User")
        return resp

##################### USER STATUSES #####################

class User_statuses(Resource):

    def get(self, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            user_statuses = g.con.get_statuses_for_user(user_id)

            items = []

            if user_statuses is not None:
                for status in user_statuses:
                    status_id = status["status_id"]
                    content = status["content"]
                    creation_time = status["creation_time"]

                    item = {}

                    item["href"] = api.url_for(Status, status_id = status_id)

                    item["data"] = [{"name" : "id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "Creator id"},
                                    {"name" : "content", "value" : content, "prompt" : "Status content"},
                                    {"name" : "creation_time", "value" : creation_time, "prompt" : "Status creation time"}]

                    item["links"] = [{"href" : api.url_for(Status_comments, status_id = status_id), "rel" : "status comments", "prompt" : "Status comments"},
                                     {"href" : api.url_for(Status_rates, status_id = status_id), "rel" : "status rates", "prompt" : "Status rates"},
                                     {"href" : api.url_for(Status_tags, status_id = status_id), "rel" : "status tags", "prompt" : "Status tags"},
                                     {"href" : api.url_for(Status_media, status_id = status_id), "rel" : "media list", "prompt" : "Status media items"}]

                    items.append(item)

            links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "author", "prompt" : "Author"}]

            template = {"data" : [{"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(User_statuses, user_id = user_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + STATUS_PROFILE)
        return resp

    def post(self, user_id):
        resp = None

        CONTENT = "content"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
                content = values_array[0]

                new_status = {"creator_id" : user_id, "content" : content}
                new_status_id = g.con.create_status(new_status)

                if new_status_id is None:
                    resp = internal_server_error()
                else:
                    new_url = api.url_for(Status, status_id = new_status_id)
                    resp = Response(status=201, headers={"Location": new_url})
            except:
                resp = bad_request()
        return resp

##################### USER FEED #####################

class User_feed(Resource):

    def get(self, user_id):
        resp = None
        try:
            limit = int(request.args.get("limit", -1))

            if g.con.get_user_information(user_id) is None:
                resp = resource_not_found(parameter_name = "User")
            else:
                user_feed = g.con.get_friends_statuses_for_user(user_id, limit)

                items = []

                if user_feed is not None:
                    for status in user_feed:
                        status_id = status["status_id"]
                        creator_id = status["creator_id"]
                        content = status["content"]
                        creation_time = status["creation_time"]

                        item = {}

                        item["href"] = api.url_for(Status, status_id = status_id)

                        item["data"] = [{"name" : "id", "value" : status_id, "prompt" : "Status id"},
                                        {"name" : "user_id", "value" : creator_id, "prompt" : "Creator id"},
                                        {"name" : "content", "value" : content, "prompt" : "Status content"},
                                        {"name" : "creation_time", "value" : creation_time, "prompt" : "Status creation time"}]

                        item["links"] = [{"href" : api.url_for(Status_comments, status_id = status_id), "rel" : "status comments", "prompt" : "Status comments"},
                                         {"href" : api.url_for(Status_rates, status_id = status_id), "rel" : "status rates", "prompt" : "Status rates"},
                                         {"href" : api.url_for(Status_tags, status_id = status_id), "rel" : "status tags", "prompt" : "Status tags"},
                                         {"href" : api.url_for(Status_media, status_id = status_id), "rel" : "media list", "prompt" : "Status media items"},
                                         {"href" : api.url_for(User_profile, user_id = creator_id), "rel" : "author", "prompt" : "Status creator profile"}]

                        items.append(item)

                links = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "user profile", "prompt" : "User profile"}]

                queries = [{"href" : api.url_for(User_feed, user_id = user_id),
                            "rel" : "search",
                            "prompt" : "Search", "data" : [{"name" : "limit", "value" : ""}]}]

                collection = {
                    "version" : API_VERSION,
                    "href" : api.url_for(User_feed, user_id = user_id),
                    "links" : links,
                    "items" : items,
                    "queries": queries
                }

                envelope = {"collection" : collection}

                resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + STATUS_PROFILE)
        except:
            resp = bad_request(parameter_name = "Feed limit")
        return resp

################################################### COMMENT METHODS DEFINITION ###################################################

##################### COMMENT #####################

class Comment(Resource):
    def get(self, comment_id):
        resp = None

        comment = g.con.get_comment(comment_id)

        if comment is None:
            resp = resource_not_found(parameter_name = "Comment", resp_type = HAL_JSON)
        else:
            status_id = comment["status_id"]
            user_id = comment["user_id"]
            content = comment["content"]
            creation_time = comment["creation_time"]

            _links = {
                "self" : {"href" : api.url_for(Comment, comment_id = comment_id), "profile" : COMMENT_PROFILE},
                "status commented" : {"href" : api.url_for(Status, status_id = status_id)},
                "author" : {"href" : api.url_for(User_profile, user_id = user_id)}
            }

            template = {"data": [{"name" : "content", "value" : "", "prompt" : "Comment content", "required" : "false"}]}

            hal = {
                "id" : comment_id,
                "status_id" : status_id,
                "user_id" : user_id,
                "content" : content,
                "creation_time" : creation_time,
                "_links" : _links,
                "template": template
            }

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, comment_id):
        resp = None
        server_error = False

        CONTENT = "content"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_comment(comment_id) is None:
            resp = resource_not_found(parameter_name = "Comment")
        else:
            request_body = request.get_json(force=True)  # Get and transform request body in JSON
            template_data = request_body["template"]["data"]  # Get data element of template
            values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
            content = values_array[0] if len(values_array) > 0 else None

            if content is not None:
                if not g.con.update_comment_content(comment_id, content):
                    resp = internal_server_error()
                    server_error = True

            if not server_error:
                resp = Response(status = 204)

        return resp

    def delete(self, comment_id):
        resp = None

        if g.con.delete_comment(comment_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Comment")
        return resp

################################################### RATE METHODS DEFINITION ###################################################

##################### RATE #####################

class Rate(Resource):
    def get(self, rate_id):
        resp = None

        rate = g.con.get_rate(rate_id)

        if rate is None:
            resp = resource_not_found(parameter_name = "Rate", resp_type = HAL_JSON)
        else:
            status_id = rate["status_id"]
            user_id = rate["user_id"]
            value = rate["rate"]

            _links = {
                "self" : {"href" : api.url_for(Rate, rate_id = rate_id), "profile" : RATE_PROFILE},
                "status rated" : {"href" : api.url_for(Status, status_id = status_id)},
                "author" : {"href" : api.url_for(User_profile, user_id = user_id)}
            }

            template = {"data": [{"name" : "value", "value" : "", "prompt" : "Rate value", "required" : "false"}]}

            hal = {
                "id" : rate_id,
                "status_id" : status_id,
                "user_id" : user_id,
                "rate" : value,
                "_links" : _links,
                "template": template
            }

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, rate_id):
        resp = None
        server_error = False

        RATE = "rate"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_rate(rate_id) is None:
            resp = resource_not_found(parameter_name = "Rate")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == RATE)
                rate = int(values_array[0]) if len(values_array) > 0 else None

                if rate is not None:
                    if rate < 0 or rate > 5:
                        resp = bad_request(parameter_name = "Rate value")
                        server_error = True
                    elif not g.con.update_rate_value(rate_id, rate):
                        resp = internal_server_error()
                        server_error = True

                if not server_error:
                    resp = Response(status = 204)
            except:
                resp = bad_request(parameter_name = "Rate")

        return resp

    def delete(self, rate_id):
        resp = None

        if g.con.delete_rate(rate_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Rate")
        return resp


################################################### STATUS METHODS DEFINITION ###################################################

##################### STATUS #####################

class Status(Resource):
    def get(self, status_id):
        resp = None

        status = g.con.get_status(status_id)

        if status is None:
            resp = resource_not_found(parameter_name = "Status", resp_type = HAL_JSON)
        else:
            creator_id = status["creator_id"]
            content = status["content"]
            creation_time = status["creation_time"]

            _links = {
                "self" : {"href" : api.url_for(Status, status_id = status_id), "profile" : STATUS_PROFILE},
                "status comments" : {"href" : api.url_for(Status_comments, status_id = status_id)},
                "status rates" : {"href" : api.url_for(Status_rates, status_id = status_id)},
                "status tags" : {"href" : api.url_for(Status_tags, status_id = status_id)},
                "status media list" : {"href" : api.url_for(Status_media, status_id = status_id)},
                "author" : {"href" : api.url_for(User_profile, user_id = creator_id)}
            }

            template = {"data": [{"name" : "content", "value" : "", "prompt" : "Status content", "required" : "false"}]}

            hal = {
                "id" : status_id,
                "user_id" : creator_id,
                "content" : content,
                "creation_time" : creation_time,
                "_links" : _links,
                "template": template
            }

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, status_id):
        resp = None
        server_error = False

        CONTENT = "content"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            request_body = request.get_json(force=True)  # Get and transform request body in JSON
            template_data = request_body["template"]["data"]  # Get data element of template
            values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
            content = values_array[0] if len(values_array) > 0 else None

            if content is not None:
                if not g.con.update_status_content(status_id, content):
                    resp = internal_server_error()
                    server_error = True

            if not server_error:
                resp = Response(status = 204)

        return resp

    def delete(self, status_id):
        resp = None

        if g.con.delete_status(status_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Status")
        return resp

##################### STATUS COMMENTS #####################

class Status_comments(Resource):

    def get(self, status_id):
        resp = None

        if g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            comments = g.con.get_comments_for_status(status_id)

            items = []

            if comments is not None:
                for comment in comments:
                    comment_id = comment["comment_id"]
                    user_id = comment["user_id"]
                    content = comment["content"]
                    creation_time = comment["creation_time"]

                    item = {}

                    item["href"] = api.url_for(Comment, comment_id = comment_id)

                    item["data"] = [{"name" : "id", "value" : comment_id, "prompt" : "Comment id"},
                                    {"name" : "status_id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "content", "value" : content, "prompt" : "Comment content"},
                                    {"name" : "creation_time", "value" : creation_time, "prompt" : "Comment creation time"}]

                    item["links"] = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "author", "prompt" : "User profile"}]

                    items.append(item)

            links = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status commented"}]

            template = {"data": [{"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                                 {"name" : "content", "value" : "", "prompt" : "Content", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Status_comments, status_id = status_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + COMMENT_PROFILE)
        return resp

    def post(self, status_id):
        resp = None

        AUTHOR = "author"
        CONTENT = "content"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == AUTHOR)
                author_id = int(values_array[0])
                values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
                content = values_array[0]

                new_comment = {"user_id" : author_id, "content" : content}
                new_comment_id = g.con.add_comment_to_status(status_id, new_comment)

                if new_comment_id is None:
                    resp = internal_server_error()
                else:
                    new_url = api.url_for(Comment, comment_id = new_comment_id)
                    resp = Response(status = 201, headers = {"Location": new_url})
            except:
                resp = bad_request(parameter_name = "Author id")
        return resp

##################### STATUS RATES #####################

class Status_rates(Resource):

    def get(self, status_id):
        resp = None

        if g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            rates = g.con.get_rates_for_status(status_id)

            items = []

            if rates is not None:
                for rate in rates:
                    rate_id = rate["rate_id"]
                    user_id = rate["user_id"]
                    rate = rate["rate"]

                    item = {}

                    item["href"] = api.url_for(Rate, rate_id = rate_id)

                    item["data"] = [{"name" : "id", "value" : rate_id, "prompt" : "Rate id"},
                                    {"name" : "status_id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "rate", "value" : rate, "prompt" : "Rate value"}]

                    item["links"] = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "author", "prompt" : "User profile"}]

                    items.append(item)

            links = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status rated"}]

            template = {"data": [{"name" : "author", "value" : "", "prompt" : "User id", "required" : "true"},
                                 {"name" : "rate", "value" : "", "prompt" : "Rate", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Status_rates, status_id = status_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + RATE_PROFILE)
        return resp


    def post(self, status_id):
        resp = None

        AUTHOR = "author"
        RATE = "rate"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == AUTHOR)
                author_id = int(values_array[0])
                values_array = list(data["value"] for data in template_data if data["name"] == RATE)
                rate = int(values_array[0])

                rates = g.con.get_rates_for_status(status_id)
                filtered_rates_list = list(rate for rate in rates if rate["user_id"] == author_id) if rates is not None else []
                if len(filtered_rates_list) > 0:
                    resp = double_resource_attribute(parameter_name = "Rate for this status")
                else:
                    new_rate = {"user_id" : author_id, "rate" : rate}
                    new_rate_id = g.con.add_rate_to_status(status_id, new_rate)

                    if new_rate_id is None:
                        resp = internal_server_error()
                    else:
                        new_url = api.url_for(Rate, rate_id = new_rate_id)
                        resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "Rate or author id")
        return resp

##################### STATUS TAGS #####################

class Status_tags(Resource):

    def get(self, status_id):
        resp = None

        if g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            tags = g.con.get_tagged_users_for_status(status_id)

            items = []

            if tags is not None:
                for tag in tags:
                    user_id = tag["user_id"]
                    first_name = tag["first_name"]
                    middle_name = tag["middle_name"]
                    surname = tag["surname"]
                    prof_picture_id = tag["prof_picture_id"]
                    age = tag["age"]
                    gender = tag["gender"]

                    item = {}

                    item["href"] = api.url_for(User_profile, user_id = user_id)

                    item["data"] = [{"name" : "id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "firstName", "value" : first_name, "prompt" : "User first name"}]
                    if middle_name is not None:
                        item["data"].append({"middle_name" : middle_name})
                    item["data"].extend([{"name" : "surname", "value" : surname, "prompt" : "User surname"},
                                         {"name" : "age", "value" : age, "prompt" : "User age"},
                                         {"name" : "gender", "value" : gender, "prompt" : "User gender"}])
                    if prof_picture_id is not None:
                        item["data"].append({"prof_picture_id" : prof_picture_id})

                    item["links"] = [{"href" : api.url_for(Status_tag, status_id = status_id, user_id = user_id), "rel" : "status tag", "prompt" : "Status tag"},
                                     {"href" : api.url_for(User_tags, user_id = user_id), "rel" : "user tags", "prompt" : "User tags"}]

                    items.append(item)

            links = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status"}]

            template = {"data": [{"name" : "user_id", "value" : "", "prompt" : "User tagged", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Status_tags, status_id = status_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + USER_PROFILE)
        return resp

    def post(self, status_id):
        resp = None

        USER_ID = "user_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == USER_ID)
                user_id = int(values_array[0])

                tags = g.con.get_tagged_users_for_status(status_id)
                filtered_tags_list = list(tag for tag in tags if tag["user_id"] == user_id) if tags is not None else []
                if len(filtered_tags_list) > 0:
                    resp = double_resource_attribute(parameter_name = "Tag for this status")
                else:
                    if not g.con.add_tag_to_status(status_id, user_id):
                        resp = internal_server_error()
                    else:
                        new_url = api.url_for(Status_tag, status_id = status_id, user_id = user_id)
                        resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "Tagged user id")
        return resp

##################### STATUS TAG #####################

class Status_tag(Resource):

    def get(self, status_id, user_id):
        resp = None

        if g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User", resp_type = HAL_JSON)
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status", resp_type = HAL_JSON)
        else:
            tags = g.con.get_tagged_users_for_status(status_id)
            filtered_status_tags = list(tag for tag in tags if tag["user_id"] == user_id) if tags is not None else []
            status_tag = filtered_status_tags[0] if len(filtered_status_tags) > 0 else None

            if status_tag is not None:
                first_name = status_tag["first_name"]
                middle_name = status_tag.get("middle_name", None)
                surname = status_tag["surname"]
                prof_picture_id = status_tag.get("prof_picture_id", None)
                age = status_tag["age"]
                gender = status_tag["gender"]

                _links = {"self" : {"href" : api.url_for(Status_tag, status_id = status_id, user_id = user_id), "profile" : USER_PROFILE},
                          "status tags" : {"href" : api.url_for(Status_tags, status_id = status_id)},
                          "status tagged" : {"href" : api.url_for(Status, status_id = status_id)},
                          "tag" : {"href" : api.url_for(User_profile, user_id = user_id)}}

                hal = {
                    "id" : user_id,
                    "firstName" : first_name,
                    "surname" : surname,
                    "age" : age,
                    "gender" : gender,
                    "_links" : _links
                }

                if middle_name is not None:
                    hal["middle_name"] = middle_name
                if prof_picture_id is not None:
                    hal["prof_picture_id"] = prof_picture_id

                resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
            else:
                resp = resource_not_found(parameter_name = "Tag", resp_type = HAL_JSON)
        return resp

    def delete(self, status_id, user_id):
        resp = None

        if g.con.delete_tag(status_id, user_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Tag")
        return resp

##################### STATUS MEDIA #####################

class Status_media(Resource):

    def get(self, status_id):
        resp = None

        if g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            media_list = g.con.get_media_for_status(status_id)

            items = []

            if media_list is not None:
                for media in media_list:
                    media_item_id = media["media_item_id"]
                    media_item_type = media["media_item_type"]
                    url = media["url"]
                    description = media["description"]

                    item = {}

                    item["href"] = api.url_for(Media_item, media_id = media_item_id)

                    item["data"] = [{"name" : "id", "value" : media_item_id, "prompt" : "Media item id"},
                                    {"name" : "media_item_type", "value" : media_item_type, "prompt" : "Media item type"},
                                    {"name" : "url", "value" : url, "prompt" : "Media item URL"},
                                    {"name" : "description", "value" :description, "prompt" : "Media item description"}]

                    items.append(item)

            links = [{"href" : api.url_for(Status, status_id = status_id), "rel" : "status", "prompt" : "Status"}]

            template = {"data": ["---BOUNDARY Content-Disposition: form-data; name = ''; filename = '' Content-Type : image/jpg Content-Transfer-Encoding: base64" +
                                "RAW DATA ---BOUNDARY"]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Status_media, status_id = status_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + MEDIA_ITEM_PROFILE)
        return resp


    def post(self, status_id):
        resp = None

        if request.headers.get("Content-Type", "") != MULTI_PART:
            resp = unsupported_media_type()
        elif g.con.get_status(status_id) is None:
            resp = resource_not_found(parameter_name = "Status")
        else:
            try:
                file = request.files["file"]
                if file and allowed_file(file.filename):                                    # Check if the file is one of the allowed types/extensions
                    filename = secure_filename(file.filename)                               # Make the filename safe, remove unsupported chars
                    file_extension = get_file_extension(filename)
                    if file_extension not in ALLOWED_EXTENSIONS:
                        resp = unsupported_media_type()
                    else:
                        file_relative_url = os.path.join(app.config["UPLOAD_FOLDER"], filename) #Get complete absolute path for the new resource
                        file_complete_url = file_relative_url[file_relative_url.find("/friendsNet"):]

                        file_type = get_file_type(file_extension)   #We are sure extension is one of the allowed extensions, so file_type will be either 0 or 1

                        new_media_item = {"media_item_type" : file_type, "url" : file_complete_url}
                        new_media_id = g.con.create_media(new_media_item)

                        if new_media_id is None:
                            resp = internal_server_error()
                        else:
                            if not g.con.add_media_to_status(status_id, new_media_id):
                                resp = internal_server_error()
                            else:
                                file.save(file_relative_url)
                                new_url = api.url_for(Media_item, media_item_id = new_media_id)
                                resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "Media item")
        return resp

################################################### FRIENDSHIP METHODS DEFINITION ###################################################

##################### FRIENDSHIP #####################

class Friendship(Resource):

    def get(self, friendship_id):
        resp = None

        friendship = g.con.get_friendship(friendship_id)

        if friendship is None:
            resp = resource_not_found(parameter_name = "Friendship", resp_type = HAL_JSON)
        else:
            user1_id = friendship["user1_id"]
            user2_id = friendship["user2_id"]
            friendship_status = friendship["friendship_status"]
            friendship_start = friendship.get("friendship_start", None)

            _links = {
                "self" : {"href" : api.url_for(Friendship, friendship_id = friendship_id), "profile" : FRIENDSHIP_PROFILE},
                "user profile" : {"href" : api.url_for(User_profile, user_id = user1_id)},
                "friend" : {"href" : api.url_for(User_profile, user_id = user2_id)}
            }

            template = {"data": [{"name" : "friendship_status", "value" : "", "prompt" : "Friendship status", "required" : "false"}]}

            hal = {
                "id" : friendship_id,
                "user1_id" : user1_id,
                "user2_id" : user2_id,
                "friendship_status" : friendship_status,
                "_links" : _links,
                "template" : template
            }

            if friendship_start is not None:
                hal["friendship_start"] = friendship_start

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, friendship_id):
        resp = None
        server_error = False

        STATUS = "friendship_status"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_friendship(friendship_id) is None:
            resp = resource_not_found(parameter_name = "Friendship")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == STATUS)
                status = int(values_array[0]) if len(values_array) > 0 else None

                #Response is ok if either status is given, and it's 1 or if it's not given at all.
                if status is not None:
                    if status == 1:
                        if not g.con.accept_friendship(friendship_id):
                            resp = internal_server_error()
                            server_error = True
                    else:
                        resp = bad_request(parameter_name = "Friendship status value")
                        server_error = True

                if not server_error:
                    resp = Response(status = 204)
            except:
                resp = bad_request(parameter_name = "Friendship status")
        return resp

    def delete(self, friendship_id):
        resp = None

        if g.con.delete_friendship(friendship_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Friendship")
        return resp

################################################### MEDIA ITEM METHODS DEFINITION ###################################################

##################### MEDIA LIST #####################

class Media_list(Resource):
    def post(self):
        resp = None

        if request.headers.get("Content-Type", "").find(MULTI_PART) == -1:                  #Checks whether correct content-type is present
            resp = unsupported_media_type()
        else:
            try:
                file = request.files[MULTIPART_FILE_KEY]                                               #Only one file per time
                if file and allowed_file(file.filename):                                    # Check if the file is one of the allowed types/extensions
                    filename = secure_filename(file.filename)                               # Make the filename safe, remove unsupported chars
                    file_extension = get_file_extension(filename)
                    if file_extension not in ALLOWED_EXTENSIONS:
                        resp = unsupported_media_type()
                    else:
                        filename = "media%s.%s" % (app.config["LAST_MEDIA_ITEM_ID"] + 1, file_extension)        #Name handled by server, so there is no possibility of two equal names

                        file_complete_url = os.path.join(app.static_folder, filename) #Get complete absolute path for the new resource
                        file_relative_url = file_complete_url[file_complete_url.find("/friendsNet"):]

                        file_type = get_file_type(file_extension)   #We are sure extension is one of the allowed extensions, so file_type will be either 0 or 1

                        new_media_item = {"media_type" : file_type, "url" : file_relative_url}
                        new_media_id = g.con.create_media(new_media_item)

                        if new_media_id is None:
                            resp = double_resource_attribute(parameter_name = "Media element with this name")
                        else:
                            app.config["LAST_MEDIA_ITEM_ID"] = app.config["LAST_MEDIA_ITEM_ID"] + 1
                            file.save(file_complete_url)        #Save file only if everything is correct
                            new_url = api.url_for(Media_item, media_id = new_media_id)
                            resp = Response(status = 201, headers = {"Location" : new_url})
            except Exception, e:
                resp = bad_request(parameter_name = "Media item")
        return resp

##################### MEDIA ITEM #####################

class Media_item(Resource):

    def get(self, media_id):
        resp = None

        media_item = g.con.get_media_item(media_id)

        if media_item is None:
            resp = resource_not_found(parameter_name = "Media item", resp_type = HAL_JSON)
        else:
            media_item_type = media_item["media_item_type"]
            url = media_item["url"]
            description = media_item["description"]

            _links = {
                "self" : {"href" : api.url_for(Media_item, media_id = media_id), "profile" : MEDIA_ITEM_PROFILE},
                "media list" : {"href" : api.url_for(Media_list)}
            }

            template = {"data": [{"name" : "description", "value" : "", "prompt" : "Media item description", "required" : "false"}]}

            hal = {
                "id" : media_id,
                "media_item_type" : media_item_type,
                "url" : url,
                "description" : description,
                "_links" : _links,
                "template" : template
            }

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, media_id):
        resp = None
        server_error = False

        DESCRIPTION = "description"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_media_item(media_id) is None:
            resp = resource_not_found(parameter_name = "Media item")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == DESCRIPTION)
                description = values_array[0] if len(values_array) > 0 else None

                if description is not None:
                    if not g.con.update_media_description(media_id, description):
                        resp = internal_server_error()
                        server_error = True

                if not server_error:
                    resp = Response(status = 204)
            except:
                resp = bad_request()
        return resp

    def delete(self, media_id):
        resp = None
        media_item = g.con.get_media_item(media_id)

        if media_item is not None:

            file_complete_url = os.path.join(app.static_folder, get_file_name(media_item["url"]))
            if g.con.delete_media_item(media_id):
                try:
                    os.remove(file_complete_url)                    #Delete the image from the filesystem
                    if media_id == app.config["LAST_MEDIA_ITEM_ID"]:
                        app.config["LAST_MEDIA_ITEM_ID"] = media_id - 1     #Decrement the id of the last item uploaded so that name can be reused
                except:
                    resp = internal_server_error()
                resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Media item")
        return resp

##################### MEDIA ITEM DATA #####################
class Media_item_data(Resource):

    def get(self, file_name):
        resp = None
        try:
            resp = send_from_directory(app.static_folder, file_name, as_attachment = True)
        except:
            resp = resource_not_found("Media item data", resp_type = HAL_JSON)
        return resp

################################################### GROUP METHODS DEFINITION ###################################################

##################### GROUP #####################

class Group(Resource):

    def get(self, group_id):
        resp = None

        group = g.con.get_information_for_group(group_id)

        if group is None:
            resp = resource_not_found(parameter_name = "Group", resp_type = HAL_JSON)
        else:
            name = group["name"]
            prof_picture_id = group["prof_picture_id"]
            privacy_level = group["privacy_level"]
            description = group["description"]

            _links = {
                "self" : {"href" : api.url_for(Group, group_id = group_id), "profile" : GROUP_PROFILE},
                "groups" : {"href" : api.url_for(Groups)},
                "group statuses" : {"href" : api.url_for(Group_statuses, group_id = group_id)},
                "group members" : {"href" : api.url_for(Group_members, group_id = group_id)},
                "group requests" : {"href" : api.url_for(Group_requests, group_id = group_id)}
            }

            template = {"data": [{"name" : "name", "value" : "", "prompt" : "Group name", "required" : "false"},
                                 {"name" : "privacy_level", "value" : "", "prompt" : "Privacy_level", "required" : "false"},
                                 {"name" : "description", "value" : "", "prompt" : "Description", "required" : "false"},
                                 {"name" : "prof_picture_id", "value" : "", "prompt" : "Prof picture id", "required" : "false"}]}

            hal = {
                "id" : group_id,
                "name" : name,
                "privacy_level" : privacy_level,
                "description" : description,
                "_links" : _links,
                "template" : template
            }

            if prof_picture_id is not None:
                hal["prof_picture_id"] = prof_picture_id

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, group_id):
        resp = None
        server_error = False

        NAME = "name"
        PRIVACY_LEVEL = "privacy_level"
        DESCRIPTION = "description"
        PROF_PICTURE_ID = "prof_picture_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == NAME)
                name = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == PRIVACY_LEVEL)
                privacy_level = int(values_array[0]) if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == DESCRIPTION)
                description = values_array[0] if len(values_array) > 0 else None
                values_array = list(data["value"] for data in template_data if data["name"] == PROF_PICTURE_ID)
                prof_picture_id = int(values_array[0]) if len(values_array) > 0 else None

                new_group = {}

                if name is not None:
                    new_group["name"] = name
                if privacy_level is not None:
                    if privacy_level < 0 or privacy_level > 2:
                        resp = bad_request(parameter_name = "Privacy level value")
                        server_error = True
                    else:
                        new_group["privacy_level"] = privacy_level
                if description is not None:
                    new_group["description"] = description
                if prof_picture_id is not None:
                    if g.con.get_media_item(prof_picture_id) is None:
                        resp = resource_not_found(parameter_name = "Media item")
                        server_error = True
                    else:
                        new_group["prof_picture_id"] = prof_picture_id

                if len(new_group) > 0 and not g.con.update_group(group_id, new_group):
                    resp = internal_server_error()
                    server_error = True

                if not server_error:
                    resp = Response(status = 204)
            except:
                resp = bad_request(parameter_name = "Privacy level")
        return resp

    def delete(self, group_id):
        resp = None

        if g.con.delete_group(group_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Group")
        return resp

##################### GROUP MEMBERS #####################

class Group_members(Resource):

    def get(self, group_id):
        resp = None

        if g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            memberships = g.con.get_members_for_group(group_id)

            items = []

            if memberships is not None:
                for membership in memberships:
                    user_id = membership["user_id"]
                    user_type = membership["administrator"]

                    item = {}

                    item["href"] = api.url_for(User_membership, user_id = user_id, group_id = group_id)

                    item["data"] = [{"name" : "id", "value" : user_id, "prompt" : "User id"},
                                    {"name" : "group_id", "value" : group_id, "prompt" : "Group id"},
                                    {"name" : "administrator", "value" : user_type, "prompt" : "Membership type"}]

                    items.append(item)

            links = [{"href" : api.url_for(Groups), "rel" : "groups","prompt" : "Groups"},
                     {"href" : api.url_for(Group, group_id = group_id), "rel" : "group", "prompt" : "Group"},
                     {"href" : api.url_for(Group_requests, group_id = group_id), "group requests" : "group requests", "prompt" : "Group requests"},
                     {"href" : api.url_for(Group_statuses, group_id = group_id), "rel" : "group statuses", "prompt" : "Group statuses"}]

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Group_members, group_id = group_id),
                "links" : links,
                "items" : items,
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_PROFILE)
        return resp

##################### GROUP REQUESTS #####################

class Group_requests(Resource):

    def get(self, group_id):
        resp = None

        if g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            requests = g.con.get_requests_for_group(group_id)

            items = []

            if requests is not None:
                for req in requests:
                    user_id = req["user_id"]

                    item = {}

                    item["href"] = api.url_for(Group_request, group_id = group_id, user_id = user_id)

                    item["data"] = [{"name" : "id", "value" : group_id, "prompt" : "Group id"},
                                    {"name" : "user_id", "value" : user_id, "prompt" : "User id"}]

                    item["links"] = [{"href" : api.url_for(User_profile, user_id = user_id), "rel" : "user profile", "prompt" : "User profile",},
                                     {"href" : api.url_for(User_memberships, user_id = user_id), "rel" : "user memberships", "prompt" : "User memberships"}]

                    items.append(item)

            links = [{"href" : api.url_for(Groups), "rel" : "groups", "prompt" : "Groups"},
                     {"href" : api.url_for(Group, group_id = group_id), "rel" : "group", "prompt" : "Group"},
                     {"href" : api.url_for(Group_members, group_id = group_id), "group members" : "group members", "prompt" : "Group members"},
                     {"href" : api.url_for(Group_statuses, group_id = group_id), "rel" : "group statuses", "prompt" : "Group statuses"}]

            template = {"data" : [{"name" : "user_id", "value" : "", "prompt" : "User requesting id", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Group_requests, group_id = group_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + GROUP_MEMBERSHIP_REQUEST_PROFILE)
        return resp

    def post(self, group_id):
        resp = None

        group = g.con.get_information_for_group(group_id)
        USER_ID = "user_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif group is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == USER_ID)
                user_id = int(values_array[0])

                requests = g.con.get_requests_for_group(group_id)
                members = g.con.get_members_for_group(group_id)
                filtered_requests_list = list(request for request in requests if request["user_id"] == user_id) if requests is not None else []
                filtered_members_list = list(membership for membership in members if membership["user_id"] == user_id) if members is not None else []

                if len(filtered_requests_list) > 0:
                    resp = double_resource_attribute(parameter_name = "Request for this group by this user")
                elif len(filtered_members_list) > 0:
                    resp = double_resource_attribute(parameter_name = "Membership between this group and this user")
                elif group is not None and group["privacy_level"] != 1:
                    resp = bad_request(parameter_name = "Privacy level value")
                else:
                    if not g.con.add_request_to_group(group_id, user_id):
                        resp = internal_server_error()
                    else:
                        new_url = api.url_for(Group_request, group_id = group_id, user_id = user_id)
                        resp = Response(status = 201, headers = {"Location" : new_url})
            except:
                resp = bad_request(parameter_name = "User id")
        return resp

##################### GROUP REQUEST #####################

class Group_request(Resource):

    def get(self, group_id, user_id):
        resp = None

        if g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group", resp_type = HAL_JSON)
        else:
            requests = g.con.get_requests_for_group(group_id)
            membership = list(membership for membership in requests if membership["user_id"] == user_id) if requests is not None else []
            membership = membership[0] if len(membership) > 0 else None

            if membership is None:
                resp = resource_not_found(parameter_name = "Membership", resp_type = HAL_JSON)
            else:
                _links = {
                    "self" : {"href" : api.url_for(Group_request, group_id = group_id, user_id = user_id), "profile" : GROUP_MEMBERSHIP_REQUEST_PROFILE},
                    "groups" : {"href" : api.url_for(Groups)},
                    "group" : {"href" : api.url_for(Group, group_id = group_id)},
                    "group members" : {"href" : api.url_for(Group_members, group_id = group_id)},
                    "group statuses" : {"href" : api.url_for(Group_statuses, group_id = group_id)},
                    "user profile" : {"href" : api.url_for(User_profile, user_id = user_id)},
                    "user memberships" : {"href" : api.url_for(User_memberships, user_id = user_id)}
                }

                template = {"data": [{"name" : "status", "value" : "", "prompt" : "Request status", "required" : "false"}]}

                hal = {
                    "id" : group_id,
                    "user_id" : user_id,
                    "_links" : _links,
                    "template" : template
                }

                resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def patch(self, group_id, user_id):
        resp = None

        STATUS_DECLINED = 0
        STATUS_ACCEPTED = 1

        STATUS = "status"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
            #If group, user or entire request doesn't exist
        elif g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        elif g.con.get_user_information(user_id) is None:
            resp = resource_not_found(parameter_name = "User")
        elif len(list(request for request in g.con.get_requests_for_group(group_id) if request["user_id"] == user_id)) == 0:
            resp = resource_not_found(parameter_name = "Request")
        else:
            try:
                request_body = request.get_json(force=True)  # Get and transform request body in JSON
                template_data = request_body["template"]["data"]  # Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == STATUS)
                status = int(values_array[0]) if len(values_array) > 0 else None

                if status == STATUS_DECLINED:
                    if not g.con.delete_group_request(group_id, user_id):
                        resp = internal_server_error()
                    else:
                        resp = Response(status = 201)
                elif status == STATUS_ACCEPTED:
                    if not g.con.accept_group_request(group_id, user_id):
                        resp = internal_server_error()
                    else:
                        new_url = api.url_for(User_membership, user_id = user_id, group_id = group_id)
                        resp = Response(status = 201, headers = {"Location" : new_url})
                elif status == None:
                    resp = Response(status = 201)
                else:
                    resp = bad_request(parameter_name = "Request status value")
            except:
                resp = bad_request(parameter_name = "Request status")
        return resp

##################### GROUP STATUSES #####################

class Group_statuses(Resource):

    def get(self, group_id):
        resp = None

        if g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            group_statuses = g.con.get_statuses_for_group(group_id)

            items = []

            if group_statuses is not None:
                for status in group_statuses:
                    status_id = status["status_id"]
                    creator_id = status["creator_id"]
                    content = status["content"]
                    creation_time = status["creation_time"]

                    item = {}

                    item["href"] = api.url_for(Status, status_id = status_id)

                    item["data"] = [{"name" : "id", "value" : status_id, "prompt" : "Status id"},
                                    {"name" : "user_id", "value" : creator_id, "prompt" : "Creator id"},
                                    {"name" : "content", "value" : content, "prompt" : "Status content"},
                                    {"name" : "creation_time", "value" : creation_time, "prompt" : "Status creation time"}]

                    item["links"] = [{"href" : api.url_for(Status_comments, status_id = status_id), "rel" : "status comments", "prompt" : "Status comments"},
                                     {"href" : api.url_for(Status_rates, status_id = status_id), "rel" : "status rates", "prompt" : "Status rates"},
                                     {"href" : api.url_for(Status_tags, status_id = status_id), "rel" : "status tags", "prompt" : "Status tags"},
                                     {"href" : api.url_for(Status_media, status_id = status_id), "rel" : "status media list", "prompt" : "Status media items"}]

                    items.append(item)

            links = [{"href" : api.url_for(Groups), "rel" : "groups", "prompt" : "Groups"},
                     {"href" : api.url_for(Group, group_id = group_id), "rel" : "group", "prompt" : "Group"},
                     {"href" : api.url_for(Group_members, group_id = group_id), "group members" : "group members", "prompt" : "Group members"},
                     {"href" : api.url_for(Group_requests, group_id = group_id), "rel" : "group requests", "prompt" : "Group requests"}]

            template = {"data" : [{"name" : "author", "value" : "", "prompt" : "Status creator id", "required" : "true"},
                                  {"name" : "content", "value" : "", "prompt" : "Status content", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Group_statuses, group_id = group_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + STATUS_PROFILE)
        return resp

    def post(self, group_id):
        resp = None

        AUTHOR = "author"
        CONTENT = "content"

        UNAUTHORIZED_ERROR_TITLE = "User not member of group."
        UNAUTHORIZED_ERROR_MESSAGE = "User doesn't belong to the group so he cannot post any statuses."

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif g.con.get_information_for_group(group_id) is None:
            resp = resource_not_found(parameter_name = "Group")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == AUTHOR)
                author_id = int(values_array[0])
                values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
                content = values_array[0]

                memberships = g.con.get_members_for_group(group_id)
                filtered_memberships_list = list(membership for membership in memberships if membership["user_id"] == author_id) if memberships is not None else []
                if g.con.get_user_information(author_id) is None:
                    resp = resource_not_found(parameter_name = "User")
                elif len(filtered_memberships_list) == 0:
                    resp = unauthorized_action(title = UNAUTHORIZED_ERROR_TITLE, message = UNAUTHORIZED_ERROR_MESSAGE)
                else:
                    new_status = {"creator_id" : author_id, "content" : content}
                    new_status_id = g.con.create_status(new_status, group_id = group_id)

                    if new_status_id is None:
                        resp = internal_server_error()
                    else:
                        new_url = api.url_for(Status, status_id = new_status_id)
                        resp = Response(status = 201, headers = {"Location": new_url})
            except:
                resp = bad_request(parameter_name = "Membership")
        return resp

##################### GROUPS #####################

class Groups(Resource):

    def post(self):
        resp = None

        NAME = "name"
        PRIVACY_LEVEL = "privacy_level"
        DESCRIPTION = "description"
        PROF_PICTURE_ID = "prof_picture_id"

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == NAME)
                name = values_array[0]
                values_array = list(data["value"] for data in template_data if data["name"] == PRIVACY_LEVEL)
                privacy_level = int(values_array[0])
                values_array = list(data["value"] for data in template_data if data["name"] == DESCRIPTION)
                description = values_array[0]
                values_array = list(data["value"] for data in template_data if data["name"] == PROF_PICTURE_ID)
                prof_picture_id = int(values_array[0]) if len(values_array) > 0 else None

                if privacy_level < 0 or privacy_level > 2:
                    resp = bad_request(parameter_name = "Privacy level value")
                else:
                    new_group = {"name" : name, "privacy_level" : privacy_level, "description" : description}

                    if prof_picture_id is not None:
                        if g.con.get_media_item(prof_picture_id) is None:
                            resp = resource_not_found(parameter_name = "Media item")
                        else:
                            new_group["prof_picture_id"] = prof_picture_id

                    new_group_id = g.con.create_group(new_group)
                    if new_group_id is None:
                            resp = internal_server_error()
                    else:
                        new_url = api.url_for(Group, group_id = new_group_id)
                        resp = Response(status = 201, headers = {"Location": new_url})
            except:
                resp = bad_request(parameter_name = "Privacy level")
        return resp

################################################### CONVERSATION METHODS DEFINITION ###################################################

##################### CONVERSATION #####################

class Conversation(Resource):

    def get(self, conversation_id):
        resp = None

        conversation = g.con.get_conversation(conversation_id)

        if conversation is None:
            resp = resource_not_found(parameter_name = "Conversation", resp_type = HAL_JSON)
        else:
            user1_id = conversation["user1_id"]
            user2_id = conversation["user2_id"]
            time_last_message = conversation["time_last_message"]

            _links = {
                "self" : {"href" : api.url_for(Conversation,conversation_id = conversation_id), "profile" : CONVERSATION_PROFILE},
                "user profile" : {"href" : api.url_for(User_profile, user_id = user1_id)},
                "user contacted profile" : {"href" : api.url_for(User_profile, user_id = user2_id)},
                "user1 conversations" : {"href" : api.url_for(User_conversations, user_id = user1_id)},
                "user2 conversations" : {"href" : api.url_for(User_conversations, user_id = user2_id)},
                "conversation messages" : {"href" : api.url_for(Conversation_messages, conversation_id = conversation_id)}
            }

            hal = {
                "id" : conversation_id,
                "user1_id" : user1_id,
                "user2_id" : user2_id,
                "time_last_message" : time_last_message,
                "_links" : _links
            }

            resp = Response(json.dumps(hal), 200, mimetype = HAL_JSON)
        return resp

    def delete(self, conversation_id):
        resp = None

        if g.con.delete_conversation(conversation_id):
            resp = Response(status = 204)
        else:
            resp = resource_not_found(parameter_name = "Conversation")
        return resp

##################### CONVERSATION MESSAGES #####################

class Conversation_messages(Resource):

    def get(self, conversation_id):
        resp = None

        if g.con.get_conversation(conversation_id) is None:
            resp = resource_not_found(parameter_name = "Conversation")
        else:
            messages = g.con.get_messages_for_conversation(conversation_id)

            items = []

            if messages is not None:
                for message in messages:
                    sender_id = message["sender_id"]
                    content = message["content"]
                    time_sent = message["time_sent"]

                    item = {}

                    item["data"] = [{"name" : "conversation_id", "value" : conversation_id, "prompt" : "Conversation id"},
                                    {"name" : "sender_id", "value" : sender_id, "prompt" : "Sender id"},
                                    {"name" : "content", "value" : content, "prompt" : "Message content"},
                                    {"name" : "time_sent", "value" : time_sent, "prompt" : "Time message sent"}]

                    items.append(item)

            conversation = g.con.get_conversation(conversation_id)          #Get both members of conversation
            user1_id = conversation["user1_id"]
            user2_id = conversation["user2_id"]

            links = [{"href" : api.url_for(Conversation, conversation_id = conversation_id), "rel" : "conversation", "prompt" : "Conversation"},
                     {"href" : api.url_for(User_conversations, user_id = user1_id), "rel" : "user conversations", "prompt" : "User1 conversations"},
                     {"href" : api.url_for(User_conversations, user_id = user2_id), "rel" : "user conversations", "prompt" : "User2 conversations"}]

            template = {"data" : [{"name" : "sender_id", "value" : "", "prompt" : "Sender id", "required" : "true"},
                                  {"name" : "content", "value" : "", "prompt" : "Content", "required" : "true"}]}

            collection = {
                "version" : API_VERSION,
                "href" : api.url_for(Conversation_messages,conversation_id = conversation_id),
                "links" : links,
                "items" : items,
                "template" : template
            }

            envelope = {"collection" : collection}

            resp = Response(json.dumps(envelope), 200, mimetype = COLLECTION_JSON + ";profile=" + MESSAGE_PROFILE)
        return resp

    def post(self, conversation_id):
        resp = None

        SENDER_ID = "sender_id"
        CONTENT = "content"

        UNAUTHORIZED_ERROR_TITLE = "User not part of conversation."
        UNAUTHORIZED_ERROR_MESSAGE = "User doesn't belong to the conversation so he cannot send any messages."

        conversation = g.con.get_conversation(conversation_id)

        if request.headers.get("Content-Type", "") != COLLECTION_JSON:
            resp = unsupported_media_type()
        elif conversation is None:
            resp = resource_not_found(parameter_name = "Conversation")
        else:
            try:
                request_body = request.get_json(force = True)                                   #Get and transform request body in JSON
                template_data = request_body["template"]["data"]                                #Get data element of template
                values_array = list(data["value"] for data in template_data if data["name"] == SENDER_ID)
                sender_id = int(values_array[0])
                values_array = list(data["value"] for data in template_data if data["name"] == CONTENT)
                content = values_array[0]

                if sender_id != conversation["user1_id"] and sender_id != conversation["user2_id"]:
                    resp = unauthorized_action(title = UNAUTHORIZED_ERROR_TITLE, message = UNAUTHORIZED_ERROR_MESSAGE)
                else:
                    new_message = {"conversation_id" : conversation_id, "sender_id" : sender_id, "content" : content}
                    new_message_id = g.con.create_message(new_message)

                    if new_message_id is None:
                        resp = internal_server_error()
                    else:
                        resp = Response(status = 200)
            except:
                resp = bad_request(parameter_name = "Sender id")
        return resp


################################################### ROUTES DEFINITION ###################################################

#User
api.add_resource(User_comments, "/friendsNet/api/users/<int:user_id>/comments/", endpoint = "user_comments")
api.add_resource(User_rates, "/friendsNet/api/users/<int:user_id>/rates/", endpoint = "user_rates")
api.add_resource(User_conversations, "/friendsNet/api/users/<int:user_id>/conversations/", endpoint = "user_conversations")
api.add_resource(User_friendships, "/friendsNet/api/users/<int:user_id>/friendships/", endpoint = "user_friendships")
api.add_resource(User_memberships, "/friendsNet/api/users/<int:user_id>/groups/", endpoint = "user_memberships")
api.add_resource(User_membership, "/friendsNet/api/users/<int:user_id>/groups/<int:group_id>/", endpoint = "user_membership")
api.add_resource(User_tags, "/friendsNet/api/users/<int:user_id>/tags/", endpoint = "user_tags")
api.add_resource(User_authentication, "/friendsNet/api/users/auth/", endpoint = "user_authentication")
api.add_resource(User_profiles, "/friendsNet/api/users/", endpoint = "user_profiles")
api.add_resource(User_profile, "/friendsNet/api/users/<int:user_id>/profile/", endpoint = "user_profile")
api.add_resource(User_statuses, "/friendsNet/api/users/<int:user_id>/statuses/", endpoint = "user_statuses")
api.add_resource(User_feed, "/friendsNet/api/users/<int:user_id>/feed/", endpoint = "user_feed")

#Comment
api.add_resource(Comment, "/friendsNet/api/comments/<int:comment_id>/", endpoint = "comment")

#Rate
api.add_resource(Rate, "/friendsNet/api/rates/<int:rate_id>/", endpoint = "rate")

#Status
api.add_resource(Status, "/friendsNet/api/statuses/<int:status_id>/", endpoint = "status")
api.add_resource(Status_comments, "/friendsNet/api/statuses/<int:status_id>/comments/", endpoint = "status_comments")
api.add_resource(Status_rates, "/friendsNet/api/statuses/<int:status_id>/rates/", endpoint = "status_rates")
api.add_resource(Status_tags, "/friendsNet/api/statuses/<int:status_id>/tags/", endpoint = "status_tags")
api.add_resource(Status_tag, "/friendsNet/api/statuses/<int:status_id>/tags/<int:user_id>/", endpoint = "status_tag")
api.add_resource(Status_media, "/friendsNet/api/statuses/<int:status_id>/media/", endpoint = "status_media")

#Friendship
api.add_resource(Friendship, "/friendsNet/api/friendships/<int:friendship_id>/", endpoint = "friendship")

#Media item
api.add_resource(Media_list, "/friendsNet/api/media/", endpoint = "media_list")
api.add_resource(Media_item, "/friendsNet/api/media/<int:media_id>/", endpoint = "media_item")
api.add_resource(Media_item_data, "/friendsNet/" + MEDIA_SAVING_FOLDER + "<file_name>", endpoint = "media_item_data")

#Group
api.add_resource(Groups, "/friendsNet/api/groups/", endpoint = "groups")
api.add_resource(Group, "/friendsNet/api/groups/<int:group_id>/", endpoint = "group")
api.add_resource(Group_members, "/friendsNet/api/groups/<int:group_id>/members/", endpoint = "group_members")
api.add_resource(Group_request, "/friendsNet/api/groups/<int:group_id>/requests/<int:user_id>/", endpoint = "group_request")
api.add_resource(Group_requests, "/friendsNet/api/groups/<int:group_id>/requests/", endpoint = "group_requests")
api.add_resource(Group_statuses, "/friendsNet/api/groups/<int:group_id>/statuses/", endpoint = "group_statuses")

#Conversation
api.add_resource(Conversation, "/friendsNet/api/conversations/<int:conversation_id>/", endpoint = "conversation")
api.add_resource(Conversation_messages, "/friendsNet/api/conversations/<int:conversation_id>/messages/", endpoint = "conversation_messages")


################################################### APPLICATION START ###################################################

if __name__ == "__main__":
    app.run()