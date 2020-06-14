CREATE DATABASE IF NOT EXISTS statbotics;
USE statbotics;
SHOW TABLES;

# get head of tables
SELECT * FROM teams;
SELECT * FROM years;
SELECT * FROM team_years;
SELECT * FROM events;
SELECT * FROM team_events;
SELECT * FROM matches;
SELECT * FROM team_matches;

# To restart process.py at a specific year
DELETE FROM team_years WHERE year_id=2020;
DELETE FROM years WHERE id=2020;

# Migrations
ALTER TABLE teams ADD district VARCHAR(10);

# Create a backup
CREATE DATABASE statbotics_backup;
CREATE TABLE statbotics_backup.teams select * from statbotics.teams;
CREATE TABLE statbotics_backup.years select * from statbotics.years;
CREATE TABLE statbotics_backup.team_years select * from statbotics.team_years;
CREATE TABLE statbotics_backup.events select * from statbotics.events;
CREATE TABLE statbotics_backup.team_events select * from statbotics.team_events;
CREATE TABLE statbotics_backup.matches select * from statbotics.matches;
CREATE TABLE statbotics_backup.team_matches select * from statbotics.team_matches;
