

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
  `Number_Ratings` INT NOT NULL,
  PRIMARY KEY (`UserId`))
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `Book` (
  `BookId` VARCHAR(20) NOT NULL,
  `BookName` VARCHAR(45) NOT NULL,
  `UnitPrice` VARCHAR(45) NOT NULL,
  `Purchase_Date` VARCHAR(10) NOT NULL,
  `HandNo` INT NOT NULL,
  `SupplierId` VARCHAR(30) NOT NULL,
  `Category` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`BookId`, `SupplierId`),
    FOREIGN KEY (`SupplierId`)
    REFERENCES `User` (`UserId`)
)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `Order` (
  `OrderId` VARCHAR(45) NOT NULL,
  `OrderDate` DATE NOT NULL,
  `User_UserId` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`OrderId`, `User_UserId`),
    FOREIGN KEY (`User_UserId`)
    REFERENCES `User` (`UserId`)
)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `Cart` (
  `CartId` INT NOT NULL,
  `NumberOfItems` VARCHAR(45) NOT NULL,
  `TotalPrice` VARCHAR(45) NOT NULL,
  `CustomerId` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`CartId`, `CustomerId`),
    FOREIGN KEY (`CustomerId`)
    REFERENCES `User` (`UserId`)
)
ENGINE = InnoDB;

