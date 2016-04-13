INSERT INTO users_credentials VALUES (NULL, "email1@gmail.com", "12345678", 1);
INSERT INTO users_credentials VALUES (NULL, "email2@yahoo.com", "abcdefgh", 2);
INSERT INTO users_credentials VALUES (NULL, "email3@hotmail.it", "asdfghjk", 3);
INSERT INTO users_credentials VALUES (NULL, "email4@live.net", "1029384756", 4);
INSERT INTO users_credentials VALUES (NULL, "email5@live.net", "102938475123123", 5);
INSERT INTO users_credentials VALUES (NULL, "email6@live.it", "921i391i231201238129038", 6);
INSERT INTO users_credentials VALUES (NULL, "email7@oulu.fi", "asldkaasldk)asd", 7);

INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media1.jpg", "Flowers are wonderful!");
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media2.jpg", "I'm singing in the rain :)");
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media3.jpg", NULL);
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media4.jpg", "Paradise...");
INSERT INTO media_items VALUES (NULL, 1, "/friendsNet/media_uploads/media5.mp4", "Best video ever");
INSERT INTO media_items VALUES (NULL, 1, "/friendsNet/media_uploads/media6.mp4", "Great video!");
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media7.jpg", NULL);
INSERT INTO media_items VALUES (NULL, 1, "/friendsNet/media_uploads/media8.mp4", NULL);
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media9.jpg", NULL);
INSERT INTO media_items VALUES (NULL, 0, "/friendsNet/media_uploads/media10.jpg", NULL);

INSERT INTO users_profiles VALUES (1, "Antonio", NULL, "Antonino", NULL, 20, 0);
INSERT INTO users_profiles VALUES (2, "Eugenio", NULL, "Leonetti", NULL, 25, 0);
INSERT INTO users_profiles VALUES (3, "Mikko", NULL, "Yliniemi", NULL, 28, 0);
INSERT INTO users_profiles VALUES (4, "Stefany", "Katherine", "Smith", NULL, 15, 1);
INSERT INTO users_profiles VALUES (5, "Mickael", NULL, "Red", NULL, 17, 0);
INSERT INTO users_profiles VALUES (6, "Trial", NULL, "User", NULL, 15, 1);
INSERT INTO users_profiles VALUES (7, "User", NULL, "Trial", NULL, 82, 0);

INSERT INTO statuses VALUES (NULL, 1, "Good morning!", 50);
INSERT INTO statuses VALUES (NULL, 1, "Good afternoon!", 80);
INSERT INTO statuses VALUES (NULL, 2, "I'm here!!!!", 90);
INSERT INTO statuses VALUES (NULL, 3, "So sleepy....", 100);
INSERT INTO statuses VALUES (NULL, 3, "Happy bday :D !", 150);
INSERT INTO statuses VALUES (NULL, 3, "Hello baby :**", 170);
INSERT INTO statuses VALUES (NULL, 4, "Robotssss", 200);
INSERT INTO statuses VALUES (NULL, 4, "Sea, peace, sun, repeat.", 230);
INSERT INTO statuses VALUES (NULL, 3, "Hello everyone :)", 1931);

INSERT INTO statuses_tags_lists VALUES (1, 2);
INSERT INTO statuses_tags_lists VALUES (1, 4);
INSERT INTO statuses_tags_lists VALUES (2, 3);
INSERT INTO statuses_tags_lists VALUES (2, 1);
INSERT INTO statuses_tags_lists VALUES (3, 3);
INSERT INTO statuses_tags_lists VALUES (4, 1);
INSERT INTO statuses_tags_lists VALUES (4, 2);

INSERT INTO statuses_media_lists VALUES (1, 1);
INSERT INTO statuses_media_lists VALUES (2, 2);
INSERT INTO statuses_media_lists VALUES (3, 3);
INSERT INTO statuses_media_lists VALUES (4, 4);
INSERT INTO statuses_media_lists VALUES (5, 5);

INSERT INTO rates VALUES (NULL, 1, 2, 4);
INSERT INTO rates VALUES (NULL, 2, 1, 4);
INSERT INTO rates VALUES (NULL, 2, 2, 4);
INSERT INTO rates VALUES (NULL, 4, 4, 4);
INSERT INTO rates VALUES (NULL, 4, 3, 4);
INSERT INTO rates VALUES (NULL, 4, 2, 4);
INSERT INTO rates VALUES (NULL, 5, 1, 4);
INSERT INTO rates VALUES (NULL, 5, 2, 4);
INSERT INTO rates VALUES (NULL, 5, 3, 4);
INSERT INTO rates VALUES (NULL, 5, 4, 4);
INSERT INTO rates VALUES (NULL, 6, 3, 4);
INSERT INTO rates VALUES (NULL, 6, 4, 4);
INSERT INTO rates VALUES (NULL, 6, 2, 4);
INSERT INTO rates VALUES (NULL, 8, 1, 4);
INSERT INTO rates VALUES (NULL, 8, 3, 4);

INSERT INTO comments VALUES (NULL, 1, 2, "Ahahahaah", 60);
INSERT INTO comments VALUES (NULL, 1, 4, "What!!?", 140);
INSERT INTO comments VALUES (NULL, 1, 2, "No comment ahah", 200);
INSERT INTO comments VALUES (NULL, 3, 1, "Stop please!", 150);
INSERT INTO comments VALUES (NULL, 3, 2, "Why?", 200);
INSERT INTO comments VALUES (NULL, 4, 1, "Hello :D !", 120);
INSERT INTO comments VALUES (NULL, 5, 3, "Ehi :)))", 155);
INSERT INTO comments VALUES (NULL, 5, 2, "Yes? :D", 170);
INSERT INTO comments VALUES (NULL, 5, 3, "Nothing ahah", 170);
INSERT INTO comments VALUES (NULL, 5, 4, "Gooooood.", 189);
INSERT INTO comments VALUES (NULL, 7, 1, "Is anyone here?!", 600);

INSERT INTO friendships VALUES (NULL, 1, 2, 1, 100);
INSERT INTO friendships VALUES (NULL, 1, 3, 1, 590);
INSERT INTO friendships VALUES (NULL, 3, 2, 0, NULL);
INSERT INTO friendships VALUES (NULL, 4, 1, 0, NULL);
INSERT INTO friendships VALUES (NULL, 4, 3, 1, 501);
INSERT INTO friendships VALUES (NULL, 5, 6, 1, 800);

INSERT INTO conversations VALUES (NULL, 1, 4, 950);
INSERT INTO conversations VALUES (NULL, 3, 2, 1000);
INSERT INTO conversations VALUES (NULL, 4, 2, 532);
INSERT INTO conversations VALUES (NULL, 3, 1, 1427);

INSERT INTO messages VALUES (NULL, 1, 1, "Hello :)", 913);
INSERT INTO messages VALUES (NULL, 1, 4, "Hi :) !", 950);
INSERT INTO messages VALUES (NULL, 2, 3, "Take a look at this!", 563);
INSERT INTO messages VALUES (NULL, 2, 2, "Wow! Really 'Great video' as in description.", 871);
INSERT INTO messages VALUES (NULL, 2, 2, "Yep! Amazing!", 1000);
INSERT INTO messages VALUES (NULL, 3, 4, "Ehi what are you doing bro=", 300);
INSERT INTO messages VALUES (NULL, 3, 2, "Nothing special. You?", 350);
INSERT INTO messages VALUES (NULL, 3, 4, "The same ahahah", 421);
INSERT INTO messages VALUES (NULL, 3, 2, "Great! Let's meet half an hour ;)", 532);
INSERT INTO messages VALUES (NULL, 4, 3, "Hi :)...", 1427);

INSERT INTO groups VALUES (NULL, "Group1", NULL, 0, "Absolutely secret group.");
INSERT INTO groups VALUES (NULL, "Group2", NULL, 1, "Absolutely closed group! Ask and maybe you'll be accepted. Or maybe not...");
INSERT INTO groups VALUES (NULL, "Group3", NULL, 2, "Opennn");

INSERT INTO groups_members_lists VALUES (1, 1, 1);
INSERT INTO groups_members_lists VALUES (1, 2, 1);
INSERT INTO groups_members_lists VALUES (1, 3, 0);
INSERT INTO groups_members_lists VALUES (2, 3, 1);

INSERT INTO groups_statuses_lists VALUES (2, 9);

INSERT INTO groups_requests_lists VALUES (2, 1);
INSERT INTO groups_requests_lists VALUES (2, 4);