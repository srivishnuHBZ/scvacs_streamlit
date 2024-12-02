# __init__.py files are required to treat directories as Python packages. They are useful for organizing your project and enabling modular imports.


SQL Server (MSSQL)
Versions Available: 2022, 2019, 2017
Key Features:
Enterprise-grade database management system.
Full integration with Microsoft tools (e.g., Power BI, Azure).
Features like in-memory processing and advanced analytics.
Best Use Cases:
Enterprise systems and reporting.
Applications requiring advanced data integration.
Business Intelligence (BI) and data warehousing.
Python Library: pyodbc, pymssql.


I want create a section for approve or reject guest (on top of Recent Guest Registrations) that recently registered which is stored to table called guest_temp. 

i attach here sql query that used to create guest_temp:
CREATE TABLE guest_temp (
name NVARCHAR(255) NOT NULL,
plate_number NVARCHAR(50) NOT NULL,
vehicle_type NVARCHAR(30),
id_number NVARCHAR(50) NOT NULL,
phone_number NVARCHAR(15),
email NVARCHAR(100),
address NVARCHAR(100),
visit_purpose NVARCHAR(255),
check_in_date DATETIME,
check_out_date DATETIME,
);

I want the the system to fetch continuously whenever this table have new entry, if got new entry then diplay name, plate_number , vehicle_type , phone_number, visit_purpose, check_in_date , check_out_date along with 2 buttons, APPROVE and REJECT

IF APPROVE = 
    then update to the guest table
    once pump the data to this guest table, DELETE the existing data from guest_temp table, 
ELSE REJECT
    then just delete the data from guest_temp table.

help me change the code logic accordingly with break into methods

i attach the query that i used to create this table:
CREATE TABLE guest (
name NVARCHAR(255) NOT NULL,
plate_number NVARCHAR(50) NOT NULL,
id_number NVARCHAR(50) NOT NULL,
phone_number NVARCHAR(15),
email NVARCHAR(255),
address NVARCHAR(255),
visit_purpose NVARCHAR(255),
check_in_date DATETIME,
check_out_date DATETIME,
);