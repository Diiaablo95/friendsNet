PRAGMA FOREIGN_KEY = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS users_profiles (	
	user_id	INTEGER NOT NULL PRIMARY KEY,
	first_name	TEXT NOT NULL,
	middle_name	TEXT,
	surname	TEXT NOT NULL,
	prof_picture_id	INTEGER,
	age	INTEGER NOT NULL,
	gender	INTEGER NOT NULL CHECK(gender >= 0 AND gender <= 2),
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(prof_picture_id) REFERENCES media_items(media_item_id) ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE IF NOT EXISTS users_credentials (
	user_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	email	TEXT NOT NULL UNIQUE,
	password	TEXT NOT NULL CHECK(length(password) >= 8),
	registration_time	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS statuses_media_lists (	
	status_id	INTEGER NOT NULL,
	media_item_id	INTEGER NOT NULL,
	PRIMARY KEY(status_id,media_item_id),
	FOREIGN KEY(status_id) REFERENCES statuses(status_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(media_item_id) REFERENCES media_items(media_item_id) ON DELETE CASCADE ON UPDATE CASCADE
) WITHOUT ROWID;

CREATE TABLE  IF NOT EXISTS statuses_tags_lists (			
	status_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	PRIMARY KEY(status_id,user_id),
	FOREIGN KEY(status_id) REFERENCES statuses(status_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) WITHOUT ROWID;

CREATE TABLE  IF NOT EXISTS statuses (					
	status_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	creator_id	INTEGER NOT NULL,
	content	TEXT,
	creation_time	INTEGER NOT NULL,
	FOREIGN KEY(creator_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS rates (						
	rate_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	status_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	rate	INTEGER NOT NULL CHECK(rate >= 0 AND rate <= 5),
	UNIQUE(status_id, user_id),
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(status_id) REFERENCES statuses(status_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS messages (					
	message_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	conversation_id	INTEGER NOT NULL,
	sender_id	INTEGER,
	content	TEXT NOT NULL,
	time_sent	INTEGER,
	FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(sender_id) REFERENCES users_credentials(user_id) ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE  IF NOT EXISTS media_items (						
	media_item_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	media_item_type	INTEGER NOT NULL CHECK(media_item_type == 0 OR media_item_type == 1),
	url	TEXT NOT NULL UNIQUE,
	description	TEXT
);

CREATE TABLE  IF NOT EXISTS groups_statuses_lists (			
	group_id	INTEGER NOT NULL,
	status_id	INTEGER NOT NULL,
	PRIMARY KEY(group_id,status_id),
	FOREIGN KEY(group_id) REFERENCES groups(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(status_id) REFERENCES statuses(status_id) ON DELETE CASCADE ON UPDATE CASCADE
) WITHOUT ROWID;

CREATE TABLE  IF NOT EXISTS groups_requests_lists (
	group_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	PRIMARY KEY(group_id,user_id),
	FOREIGN KEY(group_id) REFERENCES groups(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) WITHOUT ROWID;

CREATE TABLE  IF NOT EXISTS groups_members_lists (		
	group_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	administrator	INTEGER NOT NULL CHECK(administrator == 0 OR administrator == 1),
	PRIMARY KEY(group_id,user_id),
	FOREIGN KEY(group_id) REFERENCES groups(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS groups (						
	group_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	prof_picture_id	INTEGER,
	privacy_level	INTEGER NOT NULL CHECK(privacy_level >= 0 AND privacy_level <= 2),
	description	TEXT,
	FOREIGN KEY(prof_picture_id) REFERENCES media_items(media_item_id) ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE  IF NOT EXISTS friendships (					
	friendship_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	user1_id	INTEGER NOT NULL,
	user2_id	INTEGER NOT NULL,
	friendship_status	INTEGER NOT NULL CHECK(friendship_status == 0 OR friendship_status == 1),
	friendship_start	INTEGER,
	UNIQUE(user1_id, user2_id),
	FOREIGN KEY(user1_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(user2_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE  IF NOT EXISTS conversations (				
	conversation_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	user1_id	INTEGER,
	user2_id	INTEGER,
	time_last_message	INTEGER NOT NULL,
	UNIQUE(user1_id, user2_id),
	FOREIGN KEY(user1_id) REFERENCES users_credentials(user_id) ON DELETE SET NULL ON UPDATE SET NULL,
	FOREIGN KEY(user2_id) REFERENCES users_credentials(user_id) ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE  IF NOT EXISTS comments (					
	comment_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	status_id	INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	content	TEXT NOT NULL,
	creation_time	INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES users_credentials(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(status_id) REFERENCES statuses(status_id) ON DELETE CASCADE ON UPDATE CASCADE
);

COMMIT;
PRAGMA foreign_keys = ON;