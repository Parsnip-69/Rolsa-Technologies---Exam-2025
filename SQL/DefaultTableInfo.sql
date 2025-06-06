INSERT INTO AccountType(Type) VALUES ('Personal');
INSERT INTO AccountType(Type) VALUES ('Business');
INSERT INTO AccountType(Type) VALUES ('Staff');

INSERT INTO BookingType(Title) VALUES ('Consultation');
INSERT INTO BookingType(Title) VALUES ('Installation');
INSERT INTO BookingType(Title) VALUES ('Maintenance');
INSERT INTO BookingType(Title) VALUES ('Not Continuing');


INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('Buckingham Palace', 'The Mall', 'SW1A 1AA');
INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('Black Door', '10 Downing Street', 'SW1A 2AA');
INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('London Eye', '8 Travisstock Street', 'SE1 7PB');

INSERT INTO Products(Title, Description, Price) VALUES ('Smart Thermostat', 'Control your heating from your phone', 199.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Smart LED Lightbulb', 'Control your lighting from your phone', 19.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Smart Plug', 'Control your appliances from your phone', 9.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Solar Panels', 'Generate your own electricity', 999.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Electric Car Charger', 'Charge your car at home', 299.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Heat Pump', 'Heat your home with renewable energy', 499.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Smart Energy Meter', 'Monitor your energy usage', 49.99);
INSERT INTO Products(Title, Description, Price) VALUES ('Motion Sensor', 'Automate your lights. They will turn off when no one is there', 9.99);

DELETE FROM Account WHERE AccountID >= 3;
DELETE FROM Personal WHERE AccountID >= 2;
DELETE FROM Business WHERE AccountID >= 1;
DELETE FROM Staff WHERE AccountID >= 1;

DELETE FROM Booking WHERE BookingID > 0;
DELETE FROM BookingReport WHERE ConsultationID >= 1;
DELETE FROM StaffSchedule WHERE BookingID >= 1;


DELETE FROM Report WHERE ReportID > 0;
DELETE FROM ReportProducts WHERE ReportID > 0;

DELETE FROM EnergyUsage WHERE EnergyUsageID >= 1;
DELETE FROM EnergyItem WHERE EnergyItemID >= 1;

UPDATE Booking SET BookingTypeID = 2 WHERE BookingID = 12;


