BEGIN TRANSACTION;
CREATE TABLE activity_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT,
    username        TEXT,
    action          TEXT,
    details         TEXT
);
INSERT INTO "activity_log" VALUES(1,'2026-08-01T19:42:53','ferran','signup','{"email": "ferran.torres@gmail.com"}');
INSERT INTO "activity_log" VALUES(2,'2026-08-01T19:44:46','ferran','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 2, "total": 3, "points_earned": 4}');
INSERT INTO "activity_log" VALUES(3,'2026-08-01T19:48:19','OG','signup','{"email": "torres@gmail.com"}');
INSERT INTO "activity_log" VALUES(4,'2026-08-01T19:52:25','OG','login','{}');
INSERT INTO "activity_log" VALUES(5,'2026-08-01T19:56:44','OG','login','{}');
INSERT INTO "activity_log" VALUES(6,'2026-08-01T20:03:00','OG','tracker_transaction_added','{"type": "income", "category": "Paycheck", "amount": 50.0, "date": "2026-08-01", "note": ""}');
INSERT INTO "activity_log" VALUES(7,'2026-08-01T20:05:43','Ibrahim ','signup','{"email": "A@b.com"}');
INSERT INTO "activity_log" VALUES(8,'2026-08-01T20:06:44','Ibrahim ','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 1, "total": 3, "points_earned": 2}');
INSERT INTO "activity_log" VALUES(9,'2026-08-01T20:10:35','Og','signup','{"email": "Osama.Gomaa.us@gmail.com"}');
INSERT INTO "activity_log" VALUES(10,'2026-08-01T20:11:13','Og','tracker_transaction_added','{"type": "income", "category": "Paycheck", "amount": 59.0, "date": "2026-08-01", "note": ""}');
INSERT INTO "activity_log" VALUES(11,'2026-08-01T20:11:35','Og','tracker_goal_funded','{"goal": "Emergency Fund", "amount": 90.0}');
INSERT INTO "activity_log" VALUES(12,'2026-08-02T14:18:39','Freddy','signup','{"email": "freddy@gmail.com"}');
INSERT INTO "activity_log" VALUES(13,'2026-08-02T14:19:01','Freddy','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 2, "total": 3, "points_earned": 4}');
INSERT INTO "activity_log" VALUES(14,'2026-08-02T14:19:12','Freddy','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 3, "total": 3, "points_earned": 6}');
INSERT INTO "activity_log" VALUES(15,'2026-08-02T14:19:22','Freddy','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 3, "total": 3, "points_earned": 6}');
INSERT INTO "activity_log" VALUES(16,'2026-08-02T14:19:23','Freddy','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 3, "total": 3, "points_earned": 6}');
INSERT INTO "activity_log" VALUES(17,'2026-08-02T14:20:46','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(18,'2026-08-02T14:21:34','Freddy','profile_updated','{"display_name": "Freddy", "email": "feddy@gmail.com", "age": 18}');
INSERT INTO "activity_log" VALUES(19,'2026-08-02T14:21:35','Freddy','profile_updated','{"display_name": "Freddy", "email": "feddy@gmail.com", "age": 18}');
INSERT INTO "activity_log" VALUES(20,'2026-08-02T14:22:49','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(21,'2026-08-02T14:28:12','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(22,'2026-08-02T14:30:21','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(23,'2026-08-02T14:32:47','Freddy','tracker_goal_funded','{"goal": "Emergency Fund", "amount": 550.0}');
INSERT INTO "activity_log" VALUES(24,'2026-08-02T14:32:55','Freddy','tracker_goal_funded','{"goal": "Emergency Fund", "amount": 200.0}');
INSERT INTO "activity_log" VALUES(25,'2026-08-02T14:33:19','Freddy','tracker_goal_funded','{"goal": "Concert Trip", "amount": 200.0}');
INSERT INTO "activity_log" VALUES(26,'2026-08-02T14:33:31','Freddy','tracker_goal_funded','{"goal": "Concert Trip", "amount": 200.0}');
INSERT INTO "activity_log" VALUES(27,'2026-08-02T14:33:32','Freddy','tracker_goal_funded','{"goal": "Concert Trip", "amount": 200.0}');
INSERT INTO "activity_log" VALUES(28,'2026-08-02T14:53:56','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(29,'2026-08-02T14:54:55','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(30,'2026-08-02T15:39:26','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(31,'2026-08-02T15:45:15','Freddy','login','{}');
INSERT INTO "activity_log" VALUES(32,'2026-08-02T15:47:42','Freddy','quiz_submitted','{"unit": 1, "lesson": "1.1 Needs vs. Wants vs. Values", "correct": 3, "total": 3, "points_earned": 6}');
CREATE TABLE course_points (
    username        TEXT PRIMARY KEY REFERENCES users(username),
    points          INTEGER
);
INSERT INTO "course_points" VALUES('ferran',4);
INSERT INTO "course_points" VALUES('OG',0);
INSERT INTO "course_points" VALUES('Ibrahim ',2);
INSERT INTO "course_points" VALUES('Og',0);
INSERT INTO "course_points" VALUES('Freddy',6);
CREATE TABLE course_quiz_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT REFERENCES users(username),
    unit            INTEGER,
    lesson          TEXT,
    correct         INTEGER,
    total           INTEGER
);
INSERT INTO "course_quiz_results" VALUES(1,'ferran',1,'1.1 Needs vs. Wants vs. Values',2,3);
INSERT INTO "course_quiz_results" VALUES(2,'Ibrahim ',1,'1.1 Needs vs. Wants vs. Values',1,3);
INSERT INTO "course_quiz_results" VALUES(3,'Freddy',1,'1.1 Needs vs. Wants vs. Values',3,3);
CREATE TABLE feedback (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT REFERENCES users(username),
    rating          INTEGER,
    comment         TEXT
);
CREATE TABLE goals (
    id              INTEGER,
    username        TEXT REFERENCES users(username),
    name            TEXT,
    target          REAL,
    saved           REAL,
    PRIMARY KEY (username, id)
);
INSERT INTO "goals" VALUES(1,'ferran','Emergency Fund',1000.0,350.0);
INSERT INTO "goals" VALUES(2,'ferran','Concert Trip',300.0,120.0);
INSERT INTO "goals" VALUES(1,'OG','Emergency Fund',1000.0,350.0);
INSERT INTO "goals" VALUES(2,'OG','Concert Trip',300.0,120.0);
INSERT INTO "goals" VALUES(1,'Ibrahim ','Emergency Fund',1000.0,350.0);
INSERT INTO "goals" VALUES(2,'Ibrahim ','Concert Trip',300.0,120.0);
INSERT INTO "goals" VALUES(1,'Og','Emergency Fund',1000.0,440.0);
INSERT INTO "goals" VALUES(2,'Og','Concert Trip',300.0,120.0);
INSERT INTO "goals" VALUES(1,'Freddy','Emergency Fund',1000.0,1100.0);
INSERT INTO "goals" VALUES(2,'Freddy','Concert Trip',300.0,720.0);
CREATE TABLE help_contact_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT,
    name            TEXT,
    email           TEXT,
    message         TEXT,
    date            TEXT
);
CREATE TABLE help_questions (
    id              INTEGER PRIMARY KEY,
    question        TEXT,
    answer          TEXT,
    asker           TEXT,
    date            TEXT
);
INSERT INTO "help_questions" VALUES(1,'How do I add my first transaction?','Go to Finance Tracker → the ➕ Add tab, choose income or expense, pick a category, enter the amount, and submit.','jordan_m','2026-06-20');
INSERT INTO "help_questions" VALUES(2,'Can I redo a Life Simulation from the start?','Yes — open Life Simulation and look for the restart option on the results screen once you finish a playthrough.','amara.k','2026-06-22');
INSERT INTO "help_questions" VALUES(3,'Why is Unit 3 locked?','Only Unit 1 has full lessons written so far. Locked units show their lesson outline with a 🔒 until content is added.','dev_test','2026-06-25');
INSERT INTO "help_questions" VALUES(4,'Is my data shared with anyone else?','No — everything you enter (tracker, simulation, course progress) is stored locally per account for this prototype.','priya_s','2026-06-27');
CREATE TABLE profiles (
    username        TEXT PRIMARY KEY REFERENCES users(username),
    display_name    TEXT,
    bio             TEXT,
    email           TEXT,
    age             INTEGER,
    photo_path      TEXT
);
INSERT INTO "profiles" VALUES('ferran','ferran','','',NULL,NULL);
INSERT INTO "profiles" VALUES('OG','OG','','',NULL,NULL);
INSERT INTO "profiles" VALUES('Ibrahim ','Ibrahim ','','',NULL,NULL);
INSERT INTO "profiles" VALUES('Og','Og','','',NULL,NULL);
INSERT INTO "profiles" VALUES('Freddy','Freddy','','feddy@gmail.com',18,'C:\Users\osama\Downloads\fincoach_full_packet\assets\profile_photos\Freddy.png');
CREATE TABLE simulation_progress (
    username            TEXT PRIMARY KEY REFERENCES users(username),
    stage_index         INTEGER,
    cash                REAL,
    savings             REAL,
    debt                REAL,
    score               REAL,
    last_outcome        TEXT,
    awaiting_continue   INTEGER,
    completed           INTEGER
);
INSERT INTO "simulation_progress" VALUES('ferran',0,500.0,0.0,0.0,50.0,'',0,0);
INSERT INTO "simulation_progress" VALUES('OG',0,500.0,0.0,0.0,50.0,'',0,0);
CREATE TABLE transactions (
    id              INTEGER,
    username        TEXT REFERENCES users(username),
    date            TEXT,
    type            TEXT,
    category        TEXT,
    amount          REAL,
    note            TEXT,
    PRIMARY KEY (username, id)
);
INSERT INTO "transactions" VALUES(1,'ferran','2026-06-01','income','Paycheck',1800.0,'Monthly paycheck');
INSERT INTO "transactions" VALUES(2,'ferran','2026-06-02','expense','Rent',850.0,'June rent');
INSERT INTO "transactions" VALUES(3,'ferran','2026-06-05','expense','Groceries',145.0,'');
INSERT INTO "transactions" VALUES(4,'ferran','2026-06-10','expense','Subscriptions',32.0,'Streaming + music');
INSERT INTO "transactions" VALUES(5,'ferran','2026-06-15','income','Side Hustle',220.0,'Freelance design');
INSERT INTO "transactions" VALUES(6,'ferran','2026-06-18','expense','Transportation',90.0,'Gas + transit pass');
INSERT INTO "transactions" VALUES(1,'OG','2026-06-01','income','Paycheck',1800.0,'Monthly paycheck');
INSERT INTO "transactions" VALUES(2,'OG','2026-06-02','expense','Rent',850.0,'June rent');
INSERT INTO "transactions" VALUES(3,'OG','2026-06-05','expense','Groceries',145.0,'');
INSERT INTO "transactions" VALUES(4,'OG','2026-06-10','expense','Subscriptions',32.0,'Streaming + music');
INSERT INTO "transactions" VALUES(5,'OG','2026-06-15','income','Side Hustle',220.0,'Freelance design');
INSERT INTO "transactions" VALUES(6,'OG','2026-06-18','expense','Transportation',90.0,'Gas + transit pass');
INSERT INTO "transactions" VALUES(7,'OG','2026-08-01','income','Paycheck',50.0,'');
INSERT INTO "transactions" VALUES(1,'Ibrahim ','2026-06-01','income','Paycheck',1800.0,'Monthly paycheck');
INSERT INTO "transactions" VALUES(2,'Ibrahim ','2026-06-02','expense','Rent',850.0,'June rent');
INSERT INTO "transactions" VALUES(3,'Ibrahim ','2026-06-05','expense','Groceries',145.0,'');
INSERT INTO "transactions" VALUES(4,'Ibrahim ','2026-06-10','expense','Subscriptions',32.0,'Streaming + music');
INSERT INTO "transactions" VALUES(5,'Ibrahim ','2026-06-15','income','Side Hustle',220.0,'Freelance design');
INSERT INTO "transactions" VALUES(6,'Ibrahim ','2026-06-18','expense','Transportation',90.0,'Gas + transit pass');
INSERT INTO "transactions" VALUES(1,'Og','2026-06-01','income','Paycheck',1800.0,'Monthly paycheck');
INSERT INTO "transactions" VALUES(2,'Og','2026-06-02','expense','Rent',850.0,'June rent');
INSERT INTO "transactions" VALUES(3,'Og','2026-06-05','expense','Groceries',145.0,'');
INSERT INTO "transactions" VALUES(4,'Og','2026-06-10','expense','Subscriptions',32.0,'Streaming + music');
INSERT INTO "transactions" VALUES(5,'Og','2026-06-15','income','Side Hustle',220.0,'Freelance design');
INSERT INTO "transactions" VALUES(6,'Og','2026-06-18','expense','Transportation',90.0,'Gas + transit pass');
INSERT INTO "transactions" VALUES(7,'Og','2026-08-01','income','Paycheck',59.0,'');
INSERT INTO "transactions" VALUES(1,'Freddy','2026-06-01','income','Paycheck',1800.0,'Monthly paycheck');
INSERT INTO "transactions" VALUES(2,'Freddy','2026-06-02','expense','Rent',850.0,'June rent');
INSERT INTO "transactions" VALUES(3,'Freddy','2026-06-05','expense','Groceries',145.0,'');
INSERT INTO "transactions" VALUES(4,'Freddy','2026-06-10','expense','Subscriptions',32.0,'Streaming + music');
INSERT INTO "transactions" VALUES(5,'Freddy','2026-06-15','income','Side Hustle',220.0,'Freelance design');
INSERT INTO "transactions" VALUES(6,'Freddy','2026-06-18','expense','Transportation',90.0,'Gas + transit pass');
CREATE TABLE users (
    username        TEXT PRIMARY KEY,
    email           TEXT,
    password        TEXT
);
INSERT INTO "users" VALUES('ferran','ferran.torres@gmail.com','12345678');
INSERT INTO "users" VALUES('OG','torres@gmail.com','12589');
INSERT INTO "users" VALUES('Ibrahim ','A@b.com','123');
INSERT INTO "users" VALUES('Og','Osama.Gomaa.us@gmail.com','12345678');
INSERT INTO "users" VALUES('Freddy','freddy@gmail.com','124578');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('course_quiz_results',3);
INSERT INTO "sqlite_sequence" VALUES('activity_log',32);
COMMIT;
