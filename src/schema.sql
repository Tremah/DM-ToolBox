drop table if exists ALIGNMENT;
drop table if exists AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE;
drop table if exists CHALLENGE_RATING;
drop table if exists CLIMATE;
drop table if exists CLIMATE_X_MONTH_X_PRECIPITATION_CLASS;
drop table if exists CREATURE;
drop table if exists CREATURE_TYPE;
drop table if exists CREATURE_X_ENVIRONMENT;
drop table if exists CREATURE_X_GAME_SYSTEM;
drop table if exists DIE;
drop table if exists ENCOUNTER_TABLE;
drop table if exists ENVIRONMENT;
drop table if exists GAME_SYSTEM;
drop table if exists GAME_PARAMETER;
drop table if exists GAME_PARAMETER_TYPE;
drop table if exists GAME_PARAMETER_TYPE_DESCRIPTION;
drop table if exists MONTH;
drop table if exists PRECIPITATION_CLASS;
drop table if exists ROOM_CONTENT_X_GAME_SYSTEM;
drop table if exists WEATHER_EVENT;
drop table if exists WEATHER_EVENT_DURATION;
drop table if exists TEMPERATURE_DEVIATION_X_CLIMATE;
drop table if exists TREASURE_CATEGORY;
drop table if exists TREASURE_TYPE;
drop table if exists TREASURE_ITEM_TYPE;
drop table if exists TREASURE;
drop table if exists FOUNDRY_ITEM_KEYS;

--Data Tables

create table ALIGNMENT (
  ID integer primary key autoincrement,
  NAME varchar(50) not null
);

create table CHALLENGE_RATING (
  ID integer primary key autoincrement,
  CR varchar(3) not null,
  XP integer not null
);

create table CLIMATE (
  ID integer primary key autoincrement,
  NAME varchar(100) not null
);

create table CREATURE (
  ID integer primary key,
  NAME varchar(100) not null,
  TYPE integer not null,
  TYPE integer not null,
  SUBTYPE integer,
  CR integer,
  ALIGNMENT integer,
  SOURCE varchar(500),
  foreign key(TYPE) references CREATURE_TYPE(ID),
  foreign key(CR) references CHALLENGE_RATING(ID),
  foreign key(ALIGNMENT) references ALIGNMENT(ID)
);

create unique index "ID_IDX" on "CREATURE" (
  "ID" ASC
);

create table CREATURE_TYPE (
  ID integer primary key autoincrement,
  NAME varchar(100) not null,
  IS_SUBTYPE boolean not null
);

create table DIE (
  ID integer primary key autoincrement,
  NAME varchar(10) not null,
  FACES integer not null,
  AVERAGE_VALUE float not null
);

create table ENCOUNTER_TABLE (
  ID integer primary key,
  TABLE_NAME varchar(250) not null,
  DIE_RANGE varchar(10),
  PROBABILITY float not null,
  CREATURE_NAME varchar(100) not null,
  CREATURE_TYPE varchar(100) not null,
  CREATURE_CR   varchar(3),
  CREATURE_ALIGNMENT varchar(50) not null,
  CREATURE_ENVIRONMENT varchar(500) not null,
  CREATURE_SOURCE varchar(500)
);

create table ENVIRONMENT (
  ID integer primary key autoincrement,
  NAME varchar(100) not null
);

create table GAME_SYSTEM (
  ID integer primary key autoincrement,
  NAME varchar(250),
  NAME_SHORT varchar(30) not null
);

create table GAME_PARAMETER_TYPE (
  ID integer primary key autoincrement,
  NAME varchar(100) not null
);

create table GAME_PARAMETER_TYPE_DESCRIPTION (
  ID integer primary key autoincrement,
  TYPE integer not null,
  VALUE_1 varchar(500),
  VALUE_2 varchar(500),
  VALUE_3 varchar(500),
  VALUE_4 varchar(500),
  VALUE_5 varchar(500),
  VALUE_6 varchar(500),
  VALUE_7 varchar(500),
  VALUE_8 varchar(500),
  VALUE_9 varchar(500),
  VALUE_10 varchar(500),
  foreign key(TYPE) references GAME_PARAMETER_TYPE(ID)
);

create table GAME_PARAMETER(
  TYPE integer not null,
  ID integer not null,
  VALUE_1 varchar(250),
  VALUE_2 varchar(250),
  VALUE_3 varchar(250),
  VALUE_4 varchar(250),
  VALUE_5 varchar(250),
  VALUE_6 varchar(250),
  VALUE_7 varchar(250),
  VALUE_8 varchar(250),
  VALUE_9 varchar(250),
  VALUE_10 varchar(250),
  primary key(TYPE, ID),
  foreign key(TYPE) references GAME_PARAMETER_TYPE(ID)
);

create table MONTH (
  ID integer primary key autoincrement,
  SEQUENCE integer not null,
  NAME varchar(50) not null,
  CUSTOM integer
);

create table PRECIPITATION_CLASS (
  ID integer primary key autoincrement,
  CLASS varchar(5) not null,
  NAME varchar(50),
  PRECIPITATION varchar(100),
  WIND varchar(100),
  SOLID integer,
  HOOK integer,
  DESCRIPTION varchar(1000)
);

create table ROOM_CONTENT_X_GAME_SYSTEM (
  ID integer primary key autoincrement,
  GAME_SYSTEM integer not null,
  PROBABILITY float not null,
  CONTENT varchar(500),
  TREASURE_CHANCE float,
  foreign key(GAME_SYSTEM) references GAME_SYSTEM(ID)
);

create table WEATHER_EVENT (
  ID integer primary key autoincrement,
  NAME varchar(100),
  DESCRIPTION varchar(1000)
);

create table WEATHER_EVENT_DURATION (
  ID integer primary key autoincrement,
  WEATHER_EVENT integer,
  DURATION varchar(100),
  PROBABILITY float not null,
  foreign key(WEATHER_EVENT) references WEATHER_EVENT(ID)
);

create table TEMPERATURE_DEVIATION_X_CLIMATE (
  ID integer primary key autoincrement,
  CLIMATE integer not null,
  PROBABILITY float not null,
  DEVIATION_DEG integer not null,
  DEVIATION_F integer not null,
  foreign key(CLIMATE) references CLIMATE(ID)
);

create table FOUNDRY_ITEM_KEYS (
  ID integer primary key autoincrement,
  ITEM_NAME varchar(200),
  KEY varchar(16)
);


--Junction Tables

create table CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (
  ID integer primary key autoincrement,
  CLIMATE integer not null,
  MONTH integer not null,
  PRECIPITATION_CLASS integer not null,
  PROBABILITY float not null,
  foreign key(CLIMATE) references CLIMATE(ID),
  foreign key(MONTH) references MONTH(ID),
  foreign key(PRECIPITATION_CLASS) references PRECIPITATION_CLASS(ID)
);

create table CREATURE_X_ENVIRONMENT(
  CREATURE integer not null,
  ENVIRONMENT integer not null,
  primary key(CREATURE, ENVIRONMENT),
  foreign key(CREATURE) references CREATURE(ID),
  foreign key(ENVIRONMENT) references ENVIRONMENT(ID)
);

create table CREATURE_X_GAME_SYSTEM(
  ID integer primary key autoincrement,
  CREATURE integer not null,
  GAME_SYSTEM integer not null,
  foreign key(CREATURE) references CREATURE(ID),
  foreign key(GAME_SYSTEM) references GAME_SYSTEM(ID)
);

create table AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(
  ID integer primary key autoincrement,
  CLIMATE integer not null,
  MONTH integer not null,
  TEMPERATURE_DEG integer not null,
  TEMPERATURE_F integer not null,
  foreign key(CLIMATE) references CLIMATE(ID),
  foreign key(MONTH) references MONTH(ID)
);

--Initial Data

insert into ALIGNMENT(NAME) values('Lawful Good');
insert into ALIGNMENT(NAME) values('Lawful Neutral');
insert into ALIGNMENT(NAME) values('Lawful Evil');
insert into ALIGNMENT(NAME) values('Neutral Good');
insert into ALIGNMENT(NAME) values('Neutral');
insert into ALIGNMENT(NAME) values('Neutral Evil');
insert into ALIGNMENT(NAME) values('Chaotic Good');
insert into ALIGNMENT(NAME) values('Chaotic Neutral');
insert into ALIGNMENT(NAME) values('Chaotic Evil');
insert into ALIGNMENT(NAME) values('Unaligned');
insert into ALIGNMENT(NAME) values('Any Alignment');
insert into ALIGNMENT(NAME) values('Any Chaotic Alignment');
insert into ALIGNMENT(NAME) values('Any Lawful Alignment');
insert into ALIGNMENT(NAME) values('Any Neutral Alignment');
insert into ALIGNMENT(NAME) values('Any Good Alignment');
insert into ALIGNMENT(NAME) values('Any Evil Alignment');
insert into ALIGNMENT(NAME) values('Any Non-Good Alignment');
insert into ALIGNMENT(NAME) values('Any Non-Lawful Alignment');
insert into ALIGNMENT(NAME) values('Any Non-Evil Alignment');
insert into ALIGNMENT(NAME) values('Neutral Good Or Evil');
insert into ALIGNMENT(NAME) values('Chaotic');
insert into ALIGNMENT(NAME) values('Lawful');

insert into CHALLENGE_RATING (CR, XP) values ("0", 10);
insert into CHALLENGE_RATING (CR, XP) values ("1/8", 25);
insert into CHALLENGE_RATING (CR, XP) values ("1/4", 50);
insert into CHALLENGE_RATING (CR, XP) values ("1/2", 100);
insert into CHALLENGE_RATING (CR, XP) values ("1", 250);
insert into CHALLENGE_RATING (CR, XP) values ("2", 450);
insert into CHALLENGE_RATING (CR, XP) values ("3", 700);
insert into CHALLENGE_RATING (CR, XP) values ("4", 1100);
insert into CHALLENGE_RATING (CR, XP) values ("5", 1800);
insert into CHALLENGE_RATING (CR, XP) values ("6", 2300);
insert into CHALLENGE_RATING (CR, XP) values ("7", 2900);
insert into CHALLENGE_RATING (CR, XP) values ("8", 3900);
insert into CHALLENGE_RATING (CR, XP) values ("9", 5000);
insert into CHALLENGE_RATING (CR, XP) values ("10", 5900);
insert into CHALLENGE_RATING (CR, XP) values ("11", 7200);
insert into CHALLENGE_RATING (CR, XP) values ("12", 8400);
insert into CHALLENGE_RATING (CR, XP) values ("13", 10000);
insert into CHALLENGE_RATING (CR, XP) values ("14", 11500);
insert into CHALLENGE_RATING (CR, XP) values ("15", 13000);
insert into CHALLENGE_RATING (CR, XP) values ("16", 15000);
insert into CHALLENGE_RATING (CR, XP) values ("17", 18000);
insert into CHALLENGE_RATING (CR, XP) values ("18", 20000);
insert into CHALLENGE_RATING (CR, XP) values ("19", 22000);
insert into CHALLENGE_RATING (CR, XP) values ("20", 25000);
insert into CHALLENGE_RATING (CR, XP) values ("21", 33000);
insert into CHALLENGE_RATING (CR, XP) values ("22", 41000);
insert into CHALLENGE_RATING (CR, XP) values ("23", 50000);
insert into CHALLENGE_RATING (CR, XP) values ("24", 62000);
insert into CHALLENGE_RATING (CR, XP) values ("25", 75000);
insert into CHALLENGE_RATING (CR, XP) values ("26", 90000);
insert into CHALLENGE_RATING (CR, XP) values ("27", 105000);
insert into CHALLENGE_RATING (CR, XP) values ("28", 120000);
insert into CHALLENGE_RATING (CR, XP) values ("29", 135000);
insert into CHALLENGE_RATING (CR, XP) values ("30", 155000);

insert into CLIMATE (NAME) values ("Arctic");
insert into CLIMATE (NAME) values ("Sub-Arctic");
insert into CLIMATE (NAME) values ("Temperate");
insert into CLIMATE (NAME) values ("Sub-Tropic");
insert into CLIMATE (NAME) values ("Tropic");

insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 1, 5.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 2, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 3, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 4, 35.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 5, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 1, 6, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 1, 5.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 2, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 3, 17.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 4, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 5, 25.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 2, 6, 13.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 1, 8.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 2, 14.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 3, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 4, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 5, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 3, 6, 8.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 1, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 2, 21.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 3, 25.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 4, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 5, 18.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 4, 6, 6.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 1, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 2, 23.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 3, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 4, 18.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 5, 15.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 5, 6, 4.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 1, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 2, 34.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 3, 22.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 4, 13.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 5, 8.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 6, 6, 3.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 1, 35.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 2, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 3, 16.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 4, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 5, 6.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 7, 6, 3.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 1, 35.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 2, 26.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 3, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 4, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 5, 6.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 8, 6, 3.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 1, 15.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 2, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 3, 25.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 4, 15.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 5, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 9, 6, 5.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 1, 8.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 2, 16.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 3, 28.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 4, 25.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 5, 15.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 10, 6, 8.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 1, 5.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 2, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 3, 25.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 4, 30.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 5, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 11, 6, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 1, 5.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 2, 10.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 3, 20.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 4, 33.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 5, 22.0);
insert into CLIMATE_X_MONTH_X_PRECIPITATION_CLASS (CLIMATE, MONTH, PRECIPITATION_CLASS, PROBABILITY) values (3, 12, 6, 10.0);

insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Aberration', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Beast', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Celestial', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Construct', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Dragon', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Elemental', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Fey', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Fiend', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Giant', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Goblinoid', TRUE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Humanoid', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Monstrosity', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Ooze', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Plant', FALSE);
insert into CREATURE_TYPE(NAME, IS_SUBTYPE) values ('Undead', FALSE);

insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d2', 2, 1.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d4', 4, 2.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d6', 6, 3.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d8', 8, 4.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d10', 10, 5.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d12', 12, 6.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d20', 20, 10.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d30', 30, 15.5);
insert into DIE(NAME, FACES, AVERAGE_VALUE) values('d100', 100, 50.5);

insert into ENVIRONMENT(NAME) values('Any Environment');
insert into ENVIRONMENT(NAME) values('Arctic');
insert into ENVIRONMENT(NAME) values('Coastal');
insert into ENVIRONMENT(NAME) values('Desert');
insert into ENVIRONMENT(NAME) values('Forest');
insert into ENVIRONMENT(NAME) values('Grassland');
insert into ENVIRONMENT(NAME) values('Hill');
insert into ENVIRONMENT(NAME) values('Mountain');
insert into ENVIRONMENT(NAME) values('Plains');
insert into ENVIRONMENT(NAME) values('Planar');
insert into ENVIRONMENT(NAME) values('Swamp');
insert into ENVIRONMENT(NAME) values('Underground');
insert into ENVIRONMENT(NAME) values('Underwater');
insert into ENVIRONMENT(NAME) values('Urban');

insert into GAME_PARAMETER_TYPE(NAME) values('GAME_SYSTEM');
insert into GAME_PARAMETER_TYPE(NAME) values('DUNGEON_SIZE');
insert into GAME_PARAMETER_TYPE(NAME) values('CLIMATE');
insert into GAME_PARAMETER_TYPE(NAME) values('MONTH');
insert into GAME_PARAMETER_TYPE(NAME) values('TREASURE_ITEM_TYPE');
insert into GAME_PARAMETER_TYPE(NAME) values('TREASURE_CATEGORY');
insert into GAME_PARAMETER_TYPE(NAME) values('TREASURE_TYPE');
insert into GAME_PARAMETER_TYPE(NAME) values('TREASURE');
insert into GAME_PARAMETER_TYPE(NAME) values('GEM_VALUES');
insert into GAME_PARAMETER_TYPE(NAME) values('JEWELLERY_VALUES');
insert into GAME_PARAMETER_TYPE(NAME) values('RACE');
insert into GAME_PARAMETER_TYPE(NAME) values('CLASS');
insert into GAME_PARAMETER_TYPE(NAME) values('DUNGEON_NAME');
insert into GAME_PARAMETER_TYPE(NAME) values('TREASURE_ITEM');
insert into GAME_PARAMETER_TYPE(NAME) values('CHARACTER_ATTRIBUTES');
insert into GAME_PARAMETER_TYPE(NAME) values('LANGUAGE');
insert into GAME_PARAMETER_TYPE(NAME) values('CLASS_X_ARMOR');
insert into GAME_PARAMETER_TYPE(NAME) values('CLASS_X_WEAPON');
insert into GAME_PARAMETER_TYPE(NAME) values('CLASS_X_LANGUAGE');
insert into GAME_PARAMETER_TYPE(NAME) values('CLASS_X_PRIME_REQUISITE');

insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(1, 'Game system name (NAME)', 'Short game system name (NAME_SHORT)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3) values(2, 'Description (DESCRIPTION)', 'Number of levels (NUMBER_OF_LEVELS)', 'Number of rooms per level (NUMBER_OF_ROOMS_PER_LEVEL)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(4, 'Climate name (NAME)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3) values(5, 'Order within a year (SEQUENCE)', 'Month name (NAME)', 'Month from our world or custom months (IS_CUSTOM)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3) values(6, 'Type of treasure item (TYPE)', 'Is it a subtype (IS_SUBTYPE)', 'Parent type if it is a subtype (PARENT)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(7, 'Name of the treasure category (NAME)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 'Treasure category (CATEGORY)', 'Type of the treasure (TYPE)', 'Average value (AVERAGE_VALUE)', 'Combination of TYPE (AVERAGE VALUE) for display purposes');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3, VALUE_4, VALUE_5, VALUE_6) values(9, 'Treasure type (TYPE)', 'Treasure item type (ITEM_TYPE)', 'Treasure Item (ITEM)', 'Probability for the item to be contained in the treasure (PROBABILITY)', 'Group within the treasure (GROUP)', 'Logical operator to determine which items are in the treasure (LOGICAL_OP)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(10, 'Gem Value (VALUE)', 'Probability (PROBABILITY)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(11, 'Jewellery Value (VALUE)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(30, 'Race name (NAME)', 'Playable race (IS_PLAYABLE)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(33, 'Class name (NAME)', 'Hit die (HD)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(34, 'Dungeon name (NAME)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3) values(36, 'Item type (TYPE)', 'Item name (NAME)', 'Item value in GP (VALUE_IN_GP');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(37, 'Attribute name (NAME)', 'Attribute short name (NAME_SHORT)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1) values(38, 'Language name (NAME)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(39, 'Class (CLASS)', 'Language (LANGUAGE)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2) values(40, 'Class (CLASS)', 'PRIME_REQUISITE (PRIME_REQUISITE)');
insert into GAME_PARAMETER_TYPE_DESCRIPTION(TYPE, VALUE_1, VALUE_2, VALUE_3, VALUE_4, VALUE_5, VALUE_6) values(41, 'NAME (NAME)', 'Type (TYPE)', 'Subtype (SUBTYPE)', 'Category (CATEGORY)' 'Description (DESCRIPTION)', 'Weight (WEIGHT)', 'Cost in gp (COST)');


insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 1, 'Old School Essentials', 'OSE');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 2, 'Original Dungeons & Dragons', 'OD&D');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 3, 'Basic/Expert Dungeons & Dragons', 'B/X D&D');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 4, 'Advanced Dungeons & Dragons 1st Edition', 'AD&D 1e');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 5, 'Advanced Dungeons & Dragons 2nd Edition', 'AD&D 2e');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(1, 6, 'Dungeons & Dragons 5th Edition', 'D&D 5e');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(4, 1, 'Arctic');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(4, 2, 'Sub-Arctic');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(4, 3, 'Temperate');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(4, 4, 'Sub-Tropic');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(4, 5, 'Tropic');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 1, '1', 'January', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 2, '2', 'February', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 3, '3', 'March', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 4, '4', 'April', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 5, '5', 'May', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 6, '6', 'June', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 7, '7', 'July', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 8, '8', 'August', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 9, '9', 'September', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 10, '10', 'October', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 11, '11', 'November', '0');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(5, 12, '12', 'December', '0');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 1, 'Tiny', '1 Level', '1d6 Rooms');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 2, 'Small', '1d2 Levels', '1d6 Rooms per level');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 3, 'Medium', '1d2 + 1 Levels', '1d6 + 3 Rooms per level');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 4, 'Large', '2d2 + 2 Levels', '2d6 + 5 Rooms per level');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 5, 'Enormous', '2d4 + 3 Levels', '3d6 + 5 Rooms per level');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(2, 6, 'Gigantic', '3d6 + 5 Levels', '4d6 + 5 Rooms per level');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 1, 'Coin', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 2, 'Magic Item', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 3, 'Gem', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 4, 'Jewellery', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 5, 'Book', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 6, 'Weapon', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 7, 'Armor', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 8, 'Utensil', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 9, 'Supplies', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 10, 'Treasure Map', '0', NULL);
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 11, 'Magic Armour and Shields', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 12, 'Miscellaneous Magic Items', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 13, 'Magic Potions', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 14, 'Magic Rings', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 15, 'Magic Rods, Staves and Wands', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 16, 'Magic Scrolls and Maps', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 17, 'Magic Swords', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 18, 'Magic Weapons', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 19, 'Sentient Swords', '1', '2');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 20, 'Longsword', '1', '6');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 21, 'Crossbow', '1', '6');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3) values(6, 22, 'Chain Mail', '1', '7');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(7, 1, 'Group');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(7, 2, 'Hoard');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(7, 3, 'Individual');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 1,  '2', 'A', '18000', 'A (18000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 2,  '2', 'B', '2000',  'B (2000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 3,  '2', 'C', '1000',  'C (1000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 4,  '2', 'D', '3900',  'D (3900 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 5,  '2', 'E', '2300',  'E (2300 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 6,  '2', 'F', '7700',  'F (7700 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 7,  '2', 'G', '23000', 'G (23000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 8,  '2', 'H', '60000', 'H (60000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 9,  '2', 'I', '11000', 'I (11000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 10, '2', 'J', '25',    'J (25 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 11, '2', 'K', '180',   'K (180 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 12, '2', 'L', '240',   'L (240 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 13, '2', 'M', '50000', 'M (50000 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 14, '2', 'N', '0',     'N (0 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 15, '2', 'O', '0',     'O (0 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 16, '3', 'P', '0.1',   'P (0.1 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 17, '3', 'Q', '1',     'Q (1 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 18, '3', 'R', '3',     'R (3 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 19, '3', 'S', '5',     'S (5 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 20, '3', 'T', '17',    'T (17 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 21, '1', 'U', '160',   'U (160 GP)');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(8, 22, '1', 'V', '330',   'V (330 GP)');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 1, '1', '1', '1d6 × 1,000cp',           '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 2, '1', '1', '1d6 × 1,000sp',           '30');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 3, '1', '1', '1d4 × 1,000ep',           '20');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 4, '1', '1', '2d6 × 1,000gp',           '35');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 5, '1', '1', '1d2 × 1,000pp',           '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 6, '1', '3', '6d6 Gems',                '50');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 7, '1', '4', '6d6 Pieces Of Jewellery', '50');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 8, '1', '2', '3 Magic Items',           '30');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 9,  '2', '1', '1d8 × 1,000cp',                           '50');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 10, '2', '1', '1d6 × 1,000sp',                           '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 11, '2', '1', '1d4 × 1,000ep',                           '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 12, '2', '1', '1d3 × 1,000gp',                           '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 13, '2', '3', '1d6 gems',                                '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 14, '2', '4', '1d6 Pieces Of Jewellery',                 '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4) values(9, 15, '2', '2', '1 Magic Sword, Suit Of Armor, Or Weapon', '10');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(10, 1, '10 gp', '20');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(10, 2, '50 gp', '25');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(10, 3, '100 gp', '30');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(10, 4, '500 gp', '20');
insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2) values(10, 5, '1000 gp', '5');

insert into GAME_PARAMETER(TYPE, ID, VALUE_1) values(11, 1, '3d6 x 100 gp');

insert into MONTH(SEQUENCE, NAME, CUSTOM) values(1, 'January', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(2, 'February', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(3, 'March', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(4, 'April', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(5, 'May', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(6, 'June', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(7, 'July', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(8, 'August', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(9, 'September', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(10, 'October', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(11, 'November', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(12, 'December', 0);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(1, 'Frona', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(2, 'Mona', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(3, 'Erta', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(4, 'Skira', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(5, 'Stark', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(6, 'Sutra', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(7, 'Dusa', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(8, 'Emba', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(9, 'Thunda', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(10, 'Misto', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(11, 'Elips', 1);
insert into MONTH(SEQUENCE, NAME, CUSTOM) values(12, 'Sora', 1);

insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('A', 'None', '1d2 mm/m²', '1d2 mi/h', 0, 0, 'No storm activity. The sky is clear. No signs of precipitation or notable weather disturbances, only slight drizzle if any. Wind speeds are calm or negligible. No significant weather event to speak of.');
insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('B', 'Light', '1d6 mm/m²', '1d6 + 4 mi/h', 10, 1, 'Light rain or snow. Minimal impact on daily activities. Winds are light, barely noticeable. No significant disruptions, though roads may be damp.');
insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('C', 'Moderate', '2d6 + 4 mm/m²', '1d6 + 8 mi/h', 30, 3, 'Moderate rain or snow. Noticeable effects, may slow travel or outdoor activities. Winds are stronger, can cause discomfort. Road conditions may worsen.');
insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('D', 'Strong', '1d10 + 10 mm/m²', '1d12 + 20 mi/h', 50, 10, 'Strong storm with significant impact. Heavy rain or snow, roads may be flooded or blocked. Winds are strong, potentially damaging. Visibility may be severely reduced.');
insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('E', 'Severe', '2d20 + 15 mm/m²', '1d20 + 30 mi/h', 50, 25, 'Dangerous storm with major effects. Severe rain or snow, widespread flooding or road closures. Very strong winds, may cause structural damage. Risk of tornadoes or significant atmospheric disturbances.');
insert into PRECIPITATION_CLASS(CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION) values('F', 'Devastating', '3d20 + 35 mm/m²', '2d20 + 30 mi/h', 60, 40, 'Catastrophic storm, widespread destruction. Extremely heavy rain or snow, major flooding or snow accumulation. Destructive winds carrying debris, trees downed, major structural damage. Very high risk of tornadoes or severe weather events.');

insert into ROOM_CONTENT_X_GAME_SYSTEM(GAME_SYSTEM, PROBABILITY, CONTENT, TREASURE_CHANCE) values(1, 33.333, 'Empty', 16.666);
insert into ROOM_CONTENT_X_GAME_SYSTEM(GAME_SYSTEM, PROBABILITY, CONTENT, TREASURE_CHANCE) values(1, 33.333, 'Monster', 49.999);
insert into ROOM_CONTENT_X_GAME_SYSTEM(GAME_SYSTEM, PROBABILITY, CONTENT, TREASURE_CHANCE) values(1, 16.666, 'Special', 0);
insert into ROOM_CONTENT_X_GAME_SYSTEM(GAME_SYSTEM, PROBABILITY, CONTENT, TREASURE_CHANCE) values(1, 16.666, 'Trap', 33.333);






insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Storm', 'Typical storm bringing varying degrees of precipitation, wind, and occasional hail.');
insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Blizzard', 'Intense winter storm with heavy snowfall, sustained winds, and sub‑zero temperatures. Visibility is near zero and deep drifts can block roads.');
insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Typhoon', 'Powerful tropical cyclone over warm seas with heavy, sustained winds, torrential rain, and coastal storm surge. Can inundate shorelines and uproot structures.');
insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Tornado', 'Violent, narrow vortex from a thunderstorm with devastating winds. Touchdown causes a localized path of extreme destruction.');
insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Extratropical Cyclone', 'Large low‑pressure system bringing heavy rain or snow, strong gale‑force winds, and coastal storm surge. Impacts span large regions with broad, sustained effects.');
insert into WEATHER_EVENT(NAME, DESCRIPTION) values('Hurricane', 'Powerful tropical cyclone with sustained, strong winds, torrential rain, and coastal storm surge. Can cause flooding, wind damage, and widespread destruction.');

insert into WEATHER_EVENT_DURATION(WEATHER_EVENT, DURATION, PROBABILITY) values(1, '2 hours', 35.0);
insert into WEATHER_EVENT_DURATION(WEATHER_EVENT, DURATION, PROBABILITY) values(1, '8 hours', 30.0);
insert into WEATHER_EVENT_DURATION(WEATHER_EVENT, DURATION, PROBABILITY) values(1, '1 day', 20.0);
insert into WEATHER_EVENT_DURATION(WEATHER_EVENT, DURATION, PROBABILITY) values(1, '2 days', 10.0);
insert into WEATHER_EVENT_DURATION(WEATHER_EVENT, DURATION, PROBABILITY) values(1, 'Several days. 50% chance to continue after the second day, -10% per day.', 5.0);

insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 1, 2, 35);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 2, 4, 40);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 3, 8, 46);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 4, 13, 55);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 5, 18, 64);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 6, 21, 70);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 7, 23, 73);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 8, 23, 73);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 9, 19, 66);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 10, 13, 54);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 11, 7, 47);
insert into AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE(CLIMATE, MONTH, TEMPERATURE_DEG, TEMPERATURE_F) values(3, 12, 4, 40);

insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 5, -15, -27);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 10, -10, -18);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 25, -5, -9);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 20, 0, 0);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 25, 5, 9);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 10, 10, 18);
insert into TEMPERATURE_DEVIATION_X_CLIMATE(CLIMATE, PROBABILITY, DEVIATION_DEG, DEVIATION_F) values(3, 5, 15, 27);

insert into CREATURE(NAME, TYPE, SUBTYPE, CR, ALIGNMENT, SOURCE) values('Goblin', 11, 10, NULL, 21, 'OSE Advanced Referee Tome' );
insert into CREATURE(NAME, TYPE, SUBTYPE, CR, ALIGNMENT, SOURCE) values('Skeleton', 15, NULL, NULL, 21, 'OSE Advanced Referee Tome' );

insert into CREATURE_X_GAME_SYSTEM (CREATURE, GAME_SYSTEM)
select ID as CREATURE, 6 as GAME_SYSTEM from CREATURE
