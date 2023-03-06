### Steps to try it out:
1. Clone this repo
2. Create a conda environment using the environment.yml file and activate it
3. Run the weights.py file to downloads the weights
4. Create the required database and tables using the following MySQL queries. Also modify the username and password fields in constants.py as needed.
```MySQL
CREATE DATABASE `cyborg`;
USE `cyborg`;
CREATE TABLE `cyborg`.`members` (
  `Roll No` CHAR(9) NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Roll No`));
CREATE TABLE `cyborg`.`entries` (
  `Time` DATETIME NOT NULL,
  `Roll No` CHAR(9) NOT NULL,
  `Action` ENUM("UNLOCK", "LOCK") NOT NULL,
  PRIMARY KEY (`Time`));
```
5. Run register.py to register new users.
6. Run main.py.
