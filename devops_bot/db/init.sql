CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'repl_user';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();
CREATE TABLE Emails(
	ID SERIAL PRIMARY KEY,
	mail_addr VARCHAR(100) NOT NULL);
CREATE TABLE Phones(
        ID SERIAL PRIMARY KEY,
        phone_num VARCHAR(20) NOT NULL);
INSERT INTO Emails (mail_addr) VALUES ('example@dot.org'), ('test2@lab.dot');
INSERT INTO Phones (phone_num) VALUES ('89268290617'), ('8 (890) 863 20 19');
