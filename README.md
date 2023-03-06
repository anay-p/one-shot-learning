### Steps to try it out:
1. Clone this repository.
2. Create a conda environment using the environment.yml file and activate it.
3. Create the required database and tables using the following MySQL queries. Also modify the username and password fields in constants.py as needed.
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
4. Run register.py to register new users. Weights for models will be downloaded if running for the first time. When the 'Register' window in is focus, pressing the spacebar key with only one face being detected will register that face. Pressing 'q' will cancel registration of that user.
5. Run main.py. With the "Main" window in focus, pressing 'o' will unlock (open) the room while pressing 'c' will lock (close) the room. Pressing 'q' will quit the program.

Note: The models used can be changed in the constants.py file along with the threshold for the face recognition model.
