DROP SCHEMA IF EXISTS biosecurity;

CREATE SCHEMA biosecurity;
USE biosecurity;

/* ----- Create the tables: ----- */
CREATE TABLE IF NOT EXISTS account (
  id int NOT NULL AUTO_INCREMENT,
  username varchar(100) NOT NULL unique,
  password varchar(255) NOT NULL,
  email varchar(100) DEFAULT NULL,
  role varchar(10) default 'gardener',
  PRIMARY KEY (`id`)
);


CREATE TABLE IF NOT EXISTS gardener (
    gardener_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20),
	address VARCHAR(100),
    date_joined DATE ,
    status ENUM('active', 'inactive'),
    username VARCHAR(100) unique,
    FOREIGN KEY (username) REFERENCES account(username)
);

CREATE TABLE IF NOT EXISTS employee (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) ,
    last_name VARCHAR(50) ,
    email VARCHAR(100),
    work_phone_number VARCHAR(20) ,
    hire_date DATE,
    position VARCHAR(50) ,
    department VARCHAR(50),
    status ENUM('active', 'inactive'),
    username VARCHAR(100) unique,
    FOREIGN KEY (username) REFERENCES account(username)
);

CREATE TABLE IF NOT EXISTS weed (
    weed_id INT AUTO_INCREMENT PRIMARY KEY,
    common_name VARCHAR(100),
	weed_type VARCHAR(50),
    scientific_name VARCHAR(100),
	description TEXT,
    impacts TEXT,
    control_methods TEXT,
    images VARCHAR(255)
);



INSERT INTO account (username, password,email,role)
VALUES
('gardener', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','gardener@example.com','gardener'),
('staff', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','staff@example.com','staff'),
('admin', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','admin@example.com','admin');


INSERT INTO gardener (first_name, last_name, email , phone_number,address, date_joined, status, username)
VALUES
('John', 'Doe', 'john@example.com', '1234567890','123 Main St',  '2022-01-01', 'active', 'gardener'),
('Jane', 'Smith', 'jane@example.com', '9876543210','456 Elm St',  '2022-02-01', 'active', null),
('Michael', 'Johnson','michael@example.com', '4567890123', '789 Oak St',  '2022-03-01', 'active', null),
('Emily', 'Williams', 'emily@example.com', '2345678901','321 Pine St',  '2022-04-01', 'active', null),
('William', 'Brown', 'william@example.com', '8901234567','654 Maple St',  '2022-05-01', 'active', null);


INSERT INTO employee ( first_name, last_name, email, work_phone_number, hire_date, position, department, status, username)
VALUES
( 'Alice', 'Johnson', 'staff@example.com', '1112223333', '2022-01-01', 'employee', 'HR', 'active', 'staff'),
( 'Bob', 'Smith', 'bob@example.com', '2223334444', '2022-02-01', 'employee', 'IT', 'active', null),
( 'Charlie', 'Davis', 'charlie@example.com', '3334445555', '2022-03-01', 'employee', 'Marketing', 'active', null),
( 'Admin', 'Admin', 'admin@example.com', '4445556666', '2022-04-01', 'admin', 'Admin', 'active', 'admin');


INSERT INTO weed (common_name, weed_type, scientific_name, description, impacts, control_methods, images)
VALUES
('Aristea', 'Herb', 'Aristea ecklonii', 'description.text','impact.text', 'control.text',  'primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Arrowhead',  'Grass', 'Pseudosasa japonica',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Barberry',  'Barberry', 'Berberis glaucocarpa',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Bomarea',  'Ilstroemeria', 'Bomarea multiflora',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Cotoneaster',  'Rose', 'Cotoneaster glaucophyllus',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Elaeagnus',  'Elaeagnus', 'Elaeagnus x reflexa',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Elodea',  'Frogbit', 'Elodea canadensis',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Gypsywort',  'Mint', 'Lycopus europaeus',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Heather',  'Heath', 'Calluna vulgaris',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Hop', 'Hemp', 'Humulus lupulus',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Ivy',  'Ivy', 'Hedera helix',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Jasmine',  'Olive', 'Jasminum polyanthum',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Kikuyu',  'Grass', 'Cenchrus clandestinus',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Lantana',  'Teak', 'Lantana camara var. aculeata',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Mexican devil',  'Daisy', 'Ageratina adenophora',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Nasturtium',  'Dasturtium', 'Tropaeolum majus',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Onion weed',  'Lily', 'Allium triquetrum',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Phoenix palm', 'Palm', 'Phoenix canariensis',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Salvinia',  'Salvinia', 'Salvinia molesta',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg'),
('Stonecrop',  'Stonecrop', 'Sedum acre',  'description.text','impact.text', 'control.text','primary.jpg,image1.jpg,image2.jpg,image3.jpg')