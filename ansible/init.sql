DO
$$
BEGIN
  IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname ='repl_user') THEN
    CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'repl_user';
  END IF;
END
$$;

DO
$$
BEGIN
  IF NOT EXISTS (SELECT * FROM pg_replication_slots WHERE slot_name ='replication_slot') THEN
    SELECT pg_create_physical_replication_slot('replication_slot');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS Emails(
	ID SERIAL PRIMARY KEY,
	mail_addr VARCHAR(100) NOT NULL);
CREATE TABLE IF NOT EXISTS  Phones(
        ID SERIAL PRIMARY KEY,
        phone_num VARCHAR(20) NOT NULL);
INSERT INTO Emails (mail_addr) VALUES ('example@dot.org'), ('test2@lab.dot');
INSERT INTO Phones (phone_num) VALUES ('89268290617'), ('8 (890) 863 20 19');
