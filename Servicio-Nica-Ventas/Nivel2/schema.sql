CREATE TABLE IF NOT EXISTS location (
       id integer auto_increment,
       country varchar(2) NOT NULL,
       city varchar(100) NOT NULL,
       active bool NOT NULL,
       PRIMARY KEY (id)
) ENGINE=innodb
