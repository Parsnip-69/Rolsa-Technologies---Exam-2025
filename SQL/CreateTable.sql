DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS AccountType;
DROP TABLE IF EXISTS Booking;
DROP TABLE IF EXISTS BookingReport;
DROP TABLE IF EXISTS BookingType;
DROP TABLE IF EXISTS Business;
DROP TABLE IF EXISTS Carbon;
DROP TABLE IF EXISTS EnergyItem;
DROP TABLE IF EXISTS EnergyUsage;
DROP TABLE IF EXISTS Office;
DROP TABLE IF EXISTS PaymentStatus;
DROP TABLE IF EXISTS Personal;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Report;
DROP TABLE IF EXISTS ReportProducts;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS StaffSchedule;

CREATE TABLE Account (
    AccountID INTEGER NOT NULL,
    Email BOOLEAN DEFAULT 1,
    Password VARCHAR(255) NOT NULL,
    AccountTypeID INTEGER DEFAULT 1,
    PRIMARY KEY (AccountID),
    FOREIGN KEY (AccountTypeID) REFERENCES AccountType(AccountTypeID)
);

CREATE TABLE AccountType (
    AccountTypeID INTEGER NOT NULL,
    Type VARCHAR(25) NOT NULL,
    PRIMARY KEY (AccountTypeID)
);

CREATE TABLE Booking (
    BookingID INTEGER NOT NULL,
    BookingTypeID INTEGER NOT NULL,
    MadeDateTime DATETIME NOT NULL,
    ForDateTime DATETIME NOT NULL,
    AccountID INTEGER NOT NULL,
    PaymentStatusID INTEGER NOT NULL,
    PaymentReference VARCHAR(255) NOT NULL,
    PRIMARY KEY (BookingID),
    FOREIGN KEY (BookingTypeID) REFERENCES BookingType(BookingTypeID),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID),
    FOREIGN KEY (PaymentStatusID) REFERENCES PaymentStatus(PaymentStatusID)
);

CREATE TABLE BookingReport (
    ReportID INTEGER NOT NULL,
    ConsultationID INTEGER NOT NULL,
    FollowUpBookingID INTEGER NOT NULL,
    PRIMARY KEY (ReportID),
    FOREIGN KEY (ConsultationID) REFERENCES Booking(BookingID),
    FOREIGN KEY (FollowUpBookingID) REFERENCES Booking(BookingID)
);

CREATE TABLE BookingType (
    BookingTypeID INTEGER NOT NULL,
    Title VARCHAR(25) NOT NULL,
    PRIMARY KEY (BookingTypeID)
);

CREATE TABLE Business (
    AccountID INTEGER NOT NULL,
    Address TEXT NOT NULL,
    Postcode VARCHAR(8) NOT NULL,
    PhoneNumber VARCHAR(11) NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
);

CREATE TABLE Carbon(
    CarbonID INTEGER NOT NULL,
    CO2E FLOAT NOT NULL,
    SavedDateTime DATETIME NOT NULL,
    AccountID INTEGER NOT NULL,
    PRIMARY KEY (CarbonID)
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
);

CREATE TABLE EnergyItem(
    EnergyItemID INTEGER NOT NULL,
    EnergyUsageID INTEGER NOT NULL,
    EnergyItem VARCHAR(50) NOT NULL,
    LengthOfTime FLOAT NOT NULL,
    EnergyUsage FLOAT NOT NULL,
    PRIMARY KEY (EnergyItemID),
    FOREIGN KEY (EnergyUsageID) REFERENCES EnergyUsage(EnergyUsageID)
);

CREATE TABLE EnergyUsage(
    EnergyUsageID INTEGER NOT NULL,
    AccountID INTEGER NOT NULL,
    CreationDateTime DATETIME NOT NULL,
    PRIMARY KEY (EnergyUsageID),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
);

CREATE TABLE Office(
    OfficeID INTEGER NOT NULL,
    OfficeName VARCHAR(50) NOT NULL,
    Address TEXT NOT NULL,
    Postcode VARCHAR(8) NOT NULL,
    PRIMARY KEY (OfficeID)
);

CREATE TABLE PaymentStatus(
    PaymentStatusID INTEGER NOT NULL,
    Title VARCHAR(25) NOT NULL,
    PRIMARY KEY (PaymentStatusID)
);

CREATE TABLE Personal(
    AccountID INTEGER NOT NULL,
    FullName VARCHAR(255) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Address TEXT NOT NULL,
    Postcode VARCHAR(8) NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
);

CREATE TABLE Products(
    ProductID INTEGER NOT NULL,
    Title VARCHAR(50) NOT NULL,
    Description TEXT NOT NULL,
    Price FLOAT NOT NULL,
    PRIMARY KEY (ProductID)
);

CREATE TABLE Report(
    ReportID INTEGER NOT NULL,
    StaffID INTEGER NOT NULL,
    Description TEXT NOT NULL,
    LabourHours INTEGER NOT NULL,
    BookingTypeID INTEGER NOT NULL,
    PRIMARY KEY (ReportID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    FOREIGN KEY (BookingTypeID) REFERENCES BookingType(BookingTypeID)
);

CREATE TABLE ReportProducts(
    ProductID INTEGER NOT NULL,
    ReportID INTEGER NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (ReportID) REFERENCES Report(ReportID)
);

CREATE TABLE Staff(
    StaffID INTEGER NOT NULL,
    AccountID INTEGER NOT NULL,
    FullName VARCHAR(255) NOT NULL,
    Role VARCHAR(25) NOT NULL,
    OfficeID INTEGER NOT NULL,
    PhoneExt VARCHAR(3) NOT NULL,
    PRIMARY KEY (StaffID),
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID),
    FOREIGN KEY (OfficeID) REFERENCES Office(OfficeID)
);

CREATE TABLE StaffSchedule(
    StaffID INTEGER NOT NULL,
    ReportID INTEGER NOT NULL,
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    FOREIGN KEY (ReportID) REFERENCES Booking(BookingID)
);