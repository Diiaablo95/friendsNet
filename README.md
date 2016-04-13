#friendsNet APIs

## GENERAL DESCRIPTION

The main aim of the friendsNet social network web APIs is to <strong>allow people from different places to get in touch each other</strong>. People have to register and successively log into the platform in order to be able to use its functionalities providing an email and a password.
Although several services assolve the same job, this service is designed to provide a <strong>rapid but compact tool to share experiences</strong> with other users as well as <strong>form groups in which every member can express his own opinion</strong> and not just sharing photos, like some services do, or publishing everything on the user's profile, like other services do. Especially with the idea of groups, <strong>administrators and members</strong> in general <strong>can control</strong> who are the members of the group so that <strong>information shared</strong> is available and belong to only members of that particular group, with no access from the outside.
In the same way, a service like the last statuses posted by a user's friends let the user to be always up to date with last news from all his friends, improving significantly the enjoyability of this social experience.
Every <strong>user</strong> can <strong>post</strong> new statuses on their profiles and <strong>update/remove previous ones</strong>. Moreover, users can <strong>update their own profile picture, add/remove people to/from their friends</strong> or <strong>canceling pending requests, create/delete a group, add/remove themselves or other members to/from the group</strong> as well as <strong>accept requests from other users</strong> and <strong>change the group picture, comment/rate their own statuses and their friends&lsquo; statuses, search other users</strong> by their names, <strong>send/receive private messages to/from any friend</strong> and <strong>start a conversation</strong>.

## MAIN CONCEPTS AND RELATIONS

Every <strong>user</strong> has his own <strong>profile</strong>, and a <strong>friends&lsquo; list</strong>.
Every <strong>user&lsquo;s personal page</strong> is formed by his <strong>profile picture</strong> and a <strong>series of statutes</strong> posted by him.
Every <strong>status</strong> can have a <strong>textual description</strong>, zero or more <strong>media items</strong>, a <strong>list of friends tagged</strong>, a <strong>list of comments</strong> posted by other users and a <strong>list of rates</strong> given by other users.
Every <strong>media item</strong> can be either a <strong>photo</strong> or a <strong>video</strong> and can have a <strong>textual description</strong>.
Every <strong>group</strong> has a <strong>privacy level</strong> (e.g. public: everyone can join the group and publish new statuses; private: everyone from within the group has to accept joining requests, secret: only people from within the group can add other users). For private groups there is a list of requests.
Every <strong>group</strong> has a <strong>list of statuses</strong> posted by the members of the group, a <strong>group picture</strong>, a <strong>general description</strong> and a <strong>name</strong>.
Every <strong>comment</strong> has the <strong>commenter name</strong>, a <strong>textual content</strong> and a <strong>time of creation</strong>.
Every <strong>rate</strong> has the <strong>rater name</strong> and an <strong>integer value in the range 0-5</strong>.
The <strong>home</strong> visible by every user is formed by the <strong>most recent statuses</strong> posted by the user’s friends in their own profiles (not in groups) and this is a functionality that could be implemented by some clients since service provides this function .
Every <strong>private conversation</strong> is formed by <strong>two users</strong> and a <strong>list of messages</strong>.
Every <strong>message</strong> contain <strong>textual content</strong>. It's private: only the two users involved in the conversation can see the messages that they sent each other.

A <strong>status</strong> is a message that a user posts on his own profile or on a group and represents the main way through which users can share their information.
A <strong>group</strong> is, like the name says, a group of people who can share content available to just the members of that group, supporting than some privacy protection for statuses shared in a group. Group administrators have capabilities to remove members already inside the group as well as, depending on the group privacy level, to accept/decline new membership requests by external users and promote other members of the group as administrators.
Every <strong>rate</strong> refers to a particular status and can be given (only once per status) by another user who can have access to see that status. With the rate, the user can express his opinion about something shared by his friend and, going deeper, something like polls can be realized as well. 0 is the lowest grade while 5 is the maximum.

An unregistered user who wants to <strong>register into the platform</strong>, has to provide a valid combination of email and password that will allow him to log into the platform every time he wants;
When <strong>posting a new status</strong>, an user can enter a textual description for that status and has the possibility to link one or more media elements which can better express what are his feelings;
When <strong>searching another user</strong>, the user can provide any of this elements: name, middle name, surname. All the results that match completely or partially what he looked for will be available to the user.

## DEPENDENCIES

sqlite3 is used to handle database, so it's required to have an executable with which launching the scripts for database schema and data creation.

The modules needed in order to start the service are described in <strong>Utilities/Service_requirements.txt</strong> file. Suggestion is to set up a virtual environment where to install the components and then run the server from within the virtual environment itself.

If using <i><strong>pip</strong></i> in the virtual environment just type, from within the folder <strong>Utilities</strong>, the following line of code: <code>pip install -r Service_requirements.txt</code> to install all of the required components.

## LAUNCHING THE SERVICE

To start the server, go to the project root directory and type <code>python -m friendsNet.resources</code>. This will make the server ready to satisfy all the clients requests following the <a href = http://docs.friendsnetapis.apiary.io>documentation</a>.<br><br>

# friendsNet TEST

## DEPENDENCIES
Test suits use Python library <a href = "https://docs.python.org/2/library/unittest.html">unittest</a>. No other external library has been used up to here.<br>
Dependecies required in the previous paragraph are still required here.

## DATABASE
Database is completely handled by the testing suites that have methods to create its schema and fill it with testing data.
Database APIs module is present at path (from project root directory, in which this readme is as well) "<strong>friendsNet/database.py</strong>" while RESTful APIs module is present at path "<strong>friendsNet/resources.py</strong>".

To manually create and populate the database, move to the root project directory (containing the directories db, test, friendsNet and Utilities) and run from the console the command <code>sqlite3 DB_PATH.db</code> to launch sqlite substituing DB_PATH with the path in which you want to create the database and the name of database itself.
Once launched sqlite, type into sqlite console the commands <code>.read &ldquo;db/friendsNet_schema_db.sql&rdquo;</code> to create the schema of the database and <code>.read &ldquo;db/friendsNet_data_db.sql&rdquo;</code> to populate the database with testing values.

Otherwise, it's also possible to launch directly the script which will create the whole database: from root directory type into console (<u>not sqlite console</u>) the command <code>sqlite3 PATH_DB.db < PATH_SCRIPT.sql</code> where <i>PATH_DB.db</i> is the path and name you want to give to the database (don't forget the .db extension) and <i>PATH_SCRIPT.sql</i> is the path (relative to the actual position) to the script in <strong>db/friendsNet.sql</strong>

To examine the testing database already provided, move into db directory and type in the terminal <code>sqlite3 friendsNet.db</code>. This will launch an sqlite session with the database already populated. <strong>BE CAREFUL SINCE ALL THE TEST SUITE IS BASED ON THIS DATABASE, SO ANY MODIFIES TO THE DATABASE WILL AFFECT TESTS RESULTS!</strong><br><br>
<i style= "color : red">If you want to experiment operations on the database itself without using the APIs provided, then just create a copy of a database and launch sqlite on that copy. The same is for the files, create a copy of the media_uploads folder in order to save actual content</i>.

## LAUNCHING TESTS
To execute the tests cases for either the database interface or the RESTful services, move to the root project directory and type <code>python -m test.MODULE_TO_CALL</code> where <i>MODULE_TO_CALL</i> is the python module you want to launch to test a particular function of the service.<br>
Tests for the database interface are identified by the prefix <strong>database_abi_test</strong> and the name of the model object under testing, while tests for RESTful APIs interface are identified by the prefix <strong>services_api_test</strong> and the name of the resource under testing.

## LAUNCHING AUTOMATED TESTS
There is a way to automatically launch all the tests for either the database APIs or the RESTful APIs. To launch the script, move to the path "<strong>/friendsNet/test/automated_tests</strong>" and type <code>bash automated_test_services.txt</code> to execute all the tests for the RESTful APIs or <code>bash automated_test_db.txt</code> to execute all the tests for the database APIs.