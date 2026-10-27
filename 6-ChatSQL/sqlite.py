import sqlite3

## Connect to the SQLite database
connection=sqlite3.connect("student.db")

## Creating a cursor object to insert record,create table
cursor=connection.cursor()


## create the table 
table_info="""
create table STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""

cursor.execute(table_info)


## Insert records into the table
insert_query="""
insert into STUDENT(NAME,CLASS,SECTION,MARKS) values
('Rishabh','DATASCIENCE','A',90),
('Rohit','DATASCIENCE','B',80),
('Ramesh','DATASCIENCE','C',70),
('Suresh','DEVOPS','D',60),
('Mahesh','DEVOPS','E',50)
"""

cursor.execute(insert_query)

## Display the records from the table
print("The inserted records are:")
data=cursor.execute('''
select * from STUDENT
''')

for row in data:
    print(row)


## Commit the changes and close the connection
connection.commit()
connection.close()

