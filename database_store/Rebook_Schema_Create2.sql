-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema rebook_schema
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `rebook_schema` ;

-- -----------------------------------------------------
-- Schema rebook_schema
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rebook_schema` DEFAULT CHARACTER SET latin1 ;
USE `rebook_schema` ;

-- -----------------------------------------------------
-- Table `rebook_schema`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `User` ;

CREATE TABLE IF NOT EXISTS `User` (
  `UserId` VARCHAR(30) NOT NULL,
  `Email` VARCHAR(45) NOT NULL,
  `Name` VARCHAR(30) NOT NULL,
  `User-DOB` DATE NOT NULL,
  `Hashed_Passwd` VARCHAR(150) NOT NULL,
  `Department` VARCHAR(45) NOT NULL,
  `Programme` VARCHAR(45) NOT NULL,
  `Contact` VARCHAR(15) NOT NULL,
  `Rating` DECIMAL(1,1) NOT NULL,
  `Number_Ratings` INT(11) NOT NULL,
  PRIMARY KEY (`UserId`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Book`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Book` ;

CREATE TABLE IF NOT EXISTS `Book` (
  `BookId` VARCHAR(20) NOT NULL,
  `BookName` VARCHAR(45) NOT NULL,
  `UnitPrice` VARCHAR(45) NOT NULL,
  `Purchase_Date` DATE NOT NULL,
  `HandNo` INT(11) NOT NULL,
  `SupplierId` VARCHAR(30) NOT NULL,
  `Course` VARCHAR(45) NOT NULL,
  `Programme` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`BookId`, `SupplierId`),
  INDEX `fk_Book_User_idx` (`SupplierId` ASC),
  CONSTRAINT `fk_Book_User`
    FOREIGN KEY (`SupplierId`) REFERENCES `User` (`UserId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Cart`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Cart` ;

CREATE TABLE IF NOT EXISTS `Cart` (
  `CartId` VARCHAR(45) NOT NULL,
  `NumberOfItems` INT(11) NOT NULL,
  `TotalPrice` INT(11) NOT NULL,
  `CustomerId` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`CartId`, `CustomerId`),
  INDEX `fk_Cart_User1_idx` (`CustomerId` ASC),
  CONSTRAINT `fk_Cart_User1`
    FOREIGN KEY (`CustomerId`) REFERENCES `User` (`UserId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Cart_has_Book`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Cart_has_Book` ;

CREATE TABLE IF NOT EXISTS `Cart_has_Book` (
  `CartId` VARCHAR(45) NOT NULL,
  `Cart_UserId` VARCHAR(30) NOT NULL,
  `BookId` VARCHAR(20) NOT NULL,
  `Book_SupplierId` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`CartId`, `Cart_UserId`, `BookId`, `Book_SupplierId`),
  INDEX `fk_Cart_has_Book_Book1_idx` (`BookId` ASC, `Book_SupplierId` ASC),
  INDEX `fk_Cart_has_Book_Cart1_idx` (`CartId` ASC, `Cart_UserId` ASC),
  CONSTRAINT `fk_Cart_has_Book_Book1`
    FOREIGN KEY (`BookId` , `Book_SupplierId`)
    REFERENCES `rebook_schema`.`Book` (`BookId` , `SupplierId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Cart_has_Book_Cart1`
    FOREIGN KEY (`CartId` , `Cart_UserId`) REFERENCES `Cart` (`CartId` , `CustomerId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Order`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Order` ;

CREATE TABLE IF NOT EXISTS `Order` (
  `OrderId` VARCHAR(45) NOT NULL,
  `OrderDate` DATE NOT NULL,
  `User_UserId` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`OrderId`, `User_UserId`),
  INDEX `fk_Order_User1_idx` (`User_UserId` ASC),
  CONSTRAINT `fk_Order_User1`
    FOREIGN KEY (`User_UserId`) REFERENCES `User` (`UserId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Order_Details`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Order_Details` ;

CREATE TABLE IF NOT EXISTS `Order_Details` (
  `Order_Number` INT(11) NOT NULL AUTO_INCREMENT,
  `ReceivedDate` DATE NOT NULL,
  `Book_Received` TINYINT(4) NOT NULL,
  `Payment_Received` TINYINT(4) NOT NULL,
  `Book_BookId` VARCHAR(20) NOT NULL,
  `Book_SupplierId` VARCHAR(30) NOT NULL,
  `Order_OrderId` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Order_Number`, `Book_BookId`, `Book_SupplierId`, `Order_OrderId`),
  INDEX `fk_Order_Details_Book1_idx` (`Book_BookId` ASC, `Book_SupplierId` ASC),
  INDEX `fk_Order_Details_Order1_idx` (`Order_OrderId` ASC),
  CONSTRAINT `fk_Order_Details_Book1`
    FOREIGN KEY (`Book_BookId` , `Book_SupplierId`) REFERENCES `rebook_schema`.`Book` (`BookId` , `SupplierId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Order_Details_Order1`
    FOREIGN KEY (`Order_OrderId`) REFERENCES `Order` (`OrderId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Payment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Payment` ;

CREATE TABLE IF NOT EXISTS `Payment` (
  `Transaction_Id` VARCHAR(20) NOT NULL,
  `Amount_Received` INT(11) NOT NULL,
  `Received_Time` TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `Paid_By` VARCHAR(30) NOT NULL,
  `Payment_Medium` VARCHAR(20) NOT NULL,
  `OrderDetails_Number` INT(11) NOT NULL,
  PRIMARY KEY (`Transaction_Id`, `OrderDetails_Number`),
  INDEX `fk_Payment_Order_Details1_idx` (`OrderDetails_Number` ASC),
  CONSTRAINT `fk_Payment_Order_Details1`
    FOREIGN KEY (`OrderDetails_Number`) REFERENCES `Order_Details` (`Order_Number`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `rebook_schema`.`Forward_Payment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Forward_Payment` ;

CREATE TABLE IF NOT EXISTS `Forward_Payment` (
  `FTransaction_Id` VARCHAR(20) NOT NULL,
  `Amount_Forwarded` INT(11) NOT NULL,
  `Forwarding_Time` TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `Paid_To` VARCHAR(30) NOT NULL,
  `Payment_Medium` VARCHAR(20) NOT NULL,
  `Payment_Transaction_Id` VARCHAR(20) NOT NULL,
  `OrderDetails_Number` INT(11) NOT NULL,
  PRIMARY KEY (`FTransaction_Id`, `Payment_Transaction_Id`, `OrderDetails_Number`),
  INDEX `fk_Forward_Payment_Payment1_idx` (`Payment_Transaction_Id` ASC, `OrderDetails_Number` ASC),
  CONSTRAINT `fk_Forward_Payment_Payment1`
    FOREIGN KEY (`Payment_Transaction_Id` , `OrderDetails_Number`) REFERENCES `Payment` (`Transaction_Id` , `OrderDetails_Number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
