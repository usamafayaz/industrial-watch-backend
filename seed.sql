-- Minimal seed data. Run after "Database Script".
USE IndustrialWatchFYP;
GO

-- Rule ids 1/2/3 are hardcoded in Controllers/AutomationController.py
SET IDENTITY_INSERT ProductivityRule ON;
INSERT INTO ProductivityRule (id, name) VALUES (1, 'Smoking'), (2, 'Mobile Usage'), (3, 'Sitting');
SET IDENTITY_INSERT ProductivityRule OFF;

-- A job role named "Supervisor" gives the user the Supervisor login role
INSERT INTO JobRole (name) VALUES ('Admin'), ('Supervisor'), ('Worker');

-- Default admin login: admin / admin (change after first login)
INSERT INTO Users (username, password, user_role) VALUES ('admin', 'admin', 'Admin');
INSERT INTO Employee (name, job_role_id, job_type, date_of_joining, gender, user_id, is_guest)
VALUES ('Admin', 1, 'Full Time', GETDATE(), 'Male', SCOPE_IDENTITY(), 0);
GO
