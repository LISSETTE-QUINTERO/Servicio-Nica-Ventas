CREATE TABLE IF NOT EXISTS location (
       country varchar(2) NOT NULL,
       city varchar(100) NOT NULL,
       active bool NOT NULL,
       PRIMARY KEY (country, city)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS products (
       sku varchar (7) NOT NULL,
       description varchar(30) NOT NULL,
       price float(5) NOT NULL,
       PRIMARY KEY (sku)
) ENGINE=innodb;

CREATE TABLE IF NOT EXISTS rules (
       id INT NOT NULL AUTO_INCREMENT,
       country varchar(2) NOT NULL,
       city varchar(100) NOT NULL,
       sku varchar (7) NOT NULL,
       min_condition int(3) NOT NULL,
       max_condition int(3) NOT NULL,
       variation DECIMAL(2,1) NOT NULL,
       PRIMARY KEY (id), index (country), index(city),
       FOREIGN KEY (sku) REFERENCES products (sku),
       foreign key (country,city) REFERENCES location (country,city)
) ENGINE=innodb;

INSERT INTO products (sku, description, price) VALUES('AZ00001','Paraguas de señora estampado', 10.0);
INSERT INTO products (sku, description, price) VALUES('AZ00002','Helado de sabor fresa', 10.0);
INSERT INTO location (country, city, active) VALUES('NI','Managua', false);
INSERT INTO location (country, city, active) VALUES('NI','Nueva Guinea', false);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ00001', 500,599, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ00002', 500, 599, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ00001', 800, 804, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ00002', 800, 804, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'AZ00001', 500,599, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'AZ00002', 500, 599, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'AZ00001', 800, 804, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'AZ00002', 800, 804, 1.5); 
