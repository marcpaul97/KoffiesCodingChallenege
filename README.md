# KoffiesCodingChallenege
Solving the coding challenge at: https://github.com/KoffieLabs/backend-challenge

 There are three main scripts in this program main, sql_statements, and test_main.
 
## Main:

Main.py is where the bulk of the code is. Here we have the functions clean_VIN, check_db_for_VIN, insert_into_db, export_all_data, remove_VIN, and  call_VPIC_API_Insert_into_db. 

- **clean_VIN:** Deletes any leading/trailing whitespaces from the inputted vin. Next it makes sure the vin contains only alphanumeric characters and is exactly 17 characters long, since these were the requirements for the vin. I decided I wouldn't count a white space, as the user most likely did not intend to add a space before or after the vin.

- **check_db_for_VIN:** Does exactly what the functions name sounds like! It receives a vin, queries the SQL Lite database via the vin and returns the number of rows the vin is in. If the number of rows comes back as 1, then I return True, else if it comes back as 0, I return False, else there was a problem that happened somewhere and incorrect data has been inserted into the database. So I grab the Primary Key of the row that was created first out of the matching results from the vin and delete from the database where the vin = vin and the Primary Key does not equal the first created row. I return True after these steps have been executed, since the data is in the database.

- **insert_into_db:** Again does exactly what the functions name sounds like. It receives a dictionary with all the necessary data needed to insert into the database and attempts to insert the data into the database. If the insert changes more than 0 rows in the database, then we can assume the insert was successful and we return with a status of 201. If the insert changes less than 0 rows in the database, we can assume the insert was not successful and therefore the data was not inserted into the database, resulting in a status of 200.

- **export_all_data:** Just like the previous two functions, does exactly what the functions name describes. I query the database, selecting all information (*) from it, and utilize pandas ability to turn sql into parquet. Once the information has been changed from sql data to parquet data, I return the file in a manor that the user is able to download it.

 - **remove_VIN:** Deletes the data from the database where the database vin = the input vin. If there were any rows deleted, we change our boolean to True and return it. If there were no rows deleted, then we keep our boolean in the defaulted value of False and return the boolean.

- **call_VPIC_API_Insert_into_db:** Is the most complex function in this program. The first thing we do is clean the vin using the clean_VIN function, and then we query the database using check_db_for_VIN. If check_db_for_VIN returns true, then we select all information from the database that matches the vin, set our boolean, Cached Results = True, update our status code = 200, and return the information we gathered from the database. If check_db_for_VIN returns false, that means we need to request/call the API, convert the information the API returned to us into an easily parsable json dictionary, grab the data we want from the api and insert the data into our database using the insert_into_db function. Once we've done this, we return the information we sent to insert into the database, set our Cached Result Flag = False, and return with a status of 201.

## sql_statements:

  This is where I stored most of the sql lite statements I used. I have create_table, create_index, insert, remove, check_vin, get_earliest_created_date, and select.
  
  - **create_table:** Creates the table carFacts in the database, there's nothing fancy about this, I stored the 6 required fields with an additional carFactsID and a CreatedDate field. I did this for reasons stated above, mostly to be able to identify which rows to keep if duplicates in the database occur and for query speed.
  
  - **create_index:** Adds a unique index on the vin in the database. I added this index for two reasons, 1. Duplicate vins can now never occur, 2. I search the database by looking at the vin. Making the vin an index reduces the cost of the query signficantly and is worth the penalty when writing/updating in my opinion.
  
  - **insert:** Adds the necessary information into the database only if the vin is unique. This is tags along with the previous explanation. Since I use insert or ignore, the data will only be inserted into the database if the vin is not already present in the database.
  
  - **remove:** Deletes any data from the database where the vin equals the vin python sends to it.
  
  - **check_vin:** Selects the Primary Key where the vin equals the vin python sends to it. We only need one piece of data from each row this query returns to count the amount of times the vin is present in the database, so I queried soley for the primary key for efficiency purposes. 
  
  - **get_earliest_created_date:** Is to find the first data entry created if duplicated vins appear. We store the Primary Key and delete all the other duplicates of the vin in the database.
  
  - **select:** Is used to easily return all information required for the lookup function. I of course, use the index on the vin to search the database and return the data to be sent via the python code.
  
  
