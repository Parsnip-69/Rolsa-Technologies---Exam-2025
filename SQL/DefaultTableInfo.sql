INSERT INTO AccountType(Type) VALUES ('Personal');
INSERT INTO AccountType(Type) VALUES ('Business');
INSERT INTO AccountType(Type) VALUES ('Staff');

INSERT INTO BookingType(Title) VALUES ('Consultation');
INSERT INTO BookingType(Title) VALUES ('Installation');
INSERT INTO BookingType(Title) VALUES ('Maintainence');

INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('Buckingham Palace', 'The Mall', 'SW1A 1AA');
INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('Black Door', '10 Downing Street', 'SW1A 2AA');
INSERT INTO Office(OfficeName, Address, Postcode) VALUES ('London Eye', '8 Travisstock Street', 'SE1 7PB');

DELETE FROM Office WHERE OfficeID > 0;