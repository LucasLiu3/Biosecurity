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
    scientific_name VARCHAR(100),
    weed_type VARCHAR(50),
    description TEXT,
    impacts TEXT,
    control_methods TEXT,
    primary_image VARCHAR(255),
    images VARCHAR(255)
);


-- 为每个employee创建账号和密码
INSERT INTO account (username, password,email,role)
VALUES 
('user', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','gardener@example.com','gardener'),
('staff', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','staff@example.com','staff'),
('admin', '5fae31539e070a690c1b63720c25eb5b86084b5098a942c86c89c1d67157ed6b','admin@example.com','admin');



-- 给gardener表创建5条数据
INSERT INTO gardener (first_name, last_name, address, email, phone_number, date_joined, status, username)
VALUES 
('John', 'Doe', '123 Main St', 'john@example.com', '1234567890', '2022-01-01', 'active', 'user'),
('Jane', 'Smith', '456 Elm St', 'jane@example.com', '9876543210', '2022-02-01', 'active', null),
('Michael', 'Johnson', '789 Oak St', 'michael@example.com', '4567890123', '2022-03-01', 'active', null),
('Emily', 'Williams', '321 Pine St', 'emily@example.com', '2345678901', '2022-04-01', 'active', null),
('William', 'Brown', '654 Maple St', 'william@example.com', '8901234567', '2022-05-01', 'active', null);

-- 给employee表创建4条数据
INSERT INTO employee ( first_name, last_name, email, work_phone_number, hire_date, position, department, status, username)
VALUES 
( 'Alice', 'Johnson', 'staff@example.com', '1112223333', '2022-01-01', 'employee', 'HR', 'active', 'staff'),
( 'Bob', 'Smith', 'bob@example.com', '2223334444', '2022-02-01', 'employee', 'IT', 'active', null),
( 'Charlie', 'Davis', 'charlie@example.com', '3334445555', '2022-03-01', 'employee', 'Marketing', 'active', null),
( 'Admin', 'Admin', 'admin@example.com', '4445556666', '2022-04-01', 'admin', 'Admin', 'active', 'admin');

-- 给weed表创建20条数据
INSERT INTO weed (common_name, scientific_name, weed_type, description, impacts, control_methods, primary_image, images)
VALUES 
('Common Weed 1', 'Scientific Name 1', 'Type 1', 'Description 1', 'Impacts 1', 'Control Methods 1', 'image1.jpg', 'image1.jpg,image2.jpg,image3.jpg'),
('Common Weed 2', 'Scientific Name 2', 'Type 2', 'Description 2', 'Impacts 2', 'Control Methods 2', 'image2.jpg', 'image4.jpg,image5.jpg,image6.jpg');
-- 继续添加更多的weed数据





