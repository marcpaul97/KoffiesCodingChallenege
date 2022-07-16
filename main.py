import json
import re
import requests
import sqlite3
from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.responses import FileResponse
import sql_statements

app = FastAPI()

con = sqlite3.connect('car_facts.db')

c = con.cursor()

c.execute(sql_statements.create_table)
c.execute(sql_statements.create_index)



def clean_VIN(vin: str):
    # removing any leading/trailing spaces from the VIN
    vin = vin.strip()
    vin_length = len(vin)

    only_alpha_num = re.search("^[a-zA-Z0-9]*$", vin, flags=re.M)

    # Making sure the input is 17 letters and only contains alphanumeric numbers
    if vin_length == 17 and only_alpha_num is not None:
        return vin
    else:
        raise HTTPException(status_code=400, detail="It should contain exactly 17 alphanumeric characters.")


def check_db_for_VIN(vin: str):
    vin = clean_VIN(vin)
    try:
        # counting how many data entries there are for a specific vin
        icount = len(c.execute(sql_statements.check_vin, (vin,)).fetchall())

        if icount == 1:
            return True
        elif icount == 0:
            return False

        # if there's more than one data entry for a certain VIN, something has gone wrong, and we need to
        # clean the database. We keep the earliest entry, but delete the rest.
        else:
            first_insert = c.execute(sql_statements.get_earliest_created_date, (vin,))
            c.execute("""DELETE FROM carFacts WHERE VIN = ? AND carFactsID <> ?;""", (vin, first_insert))
            con.commit()
            num_of_deleted_rows = c.rowcount
            print(icount, " Matching data entries in database, ", num_of_deleted_rows, " have been removed")
            return True

    except sqlite3.Error as error:
        print(error)
        raise HTTPException(status_code=400, detail="Failed to check the database for records because of the error")


def insert_into_db(cf: dict):
    # inserting the data into the database if it is not already present
    try:
        c.execute(sql_statements.insert, (cf['VIN'], cf['Make'], cf['Model'], cf['Model Year'], cf['Body Class']))
        con.commit()

        num_of_inserted_records = c.rowcount

        # if there was more than 1 record inserted, then we had a successful insert
        if num_of_inserted_records > 0:
            print(num_of_inserted_records, "Record(s) have been successfully inserted to the table")

        # there were 0 records inserted, which means the data already exists in the database cache
        else:
            print("The same data has already been inserted into this database.")
    except sqlite3.Error as error:
        print(error)
        raise HTTPException(status_code=500, detail="Failed to insert the record(s) because of the error")


@app.get("/export")
async def export_all_data():
    try:

        # querying all data and dumping it into a .parquet file utilizing pandas .to_parquet
        df = pd.read_sql('SELECT * FROM carFacts', con)
        df.to_parquet('car_facts.parquet')
        print('Creation of file was successful')
    except Exception as error:
        print(error)
        raise HTTPException(status_code=418, detail="Unable to export all data because of the error")

    # returning a downloadable file of everything that was in the database cache
    return FileResponse(path='car_facts.parquet', filename='car_facts.parquet', media_type='parquet')


@app.get("/remove/{lookup_VIN}")
async def remove_VIN(lookup_VIN: str):
    cf = {'Cached Deleted': False}
    lookup_VIN = clean_VIN(lookup_VIN)

    try:
        # try to delete any data with matching VIN
        c.execute(sql_statements.remove, (lookup_VIN,))
        con.commit()
        num_of_deleted_rows = c.rowcount

        # since there was matching data, we return the information that the Cache was deleted
        if num_of_deleted_rows > 0:
            print(num_of_deleted_rows, " row of data removed with the VIN of: ", lookup_VIN)
            cf['Cached Deleted'] = True
            return cf.items()

        # There was no matching data, so we return the information that the cache was not deleted
        else:
            return cf.items()

    # error handling and returning the cache was not deleted
    except sqlite3.Error as error:
        print(error)
        raise HTTPException(status_code=400, detail="Failed to delete the record(s) because of the error")


@app.get("/lookup/{lookup_VIN}")
async def call_VPIC_API_Insert_into_db(lookup_VIN: str):
    lookup_VIN = clean_VIN(lookup_VIN)

    # checking if the VIN is already in the database
    cached_results = check_db_for_VIN(lookup_VIN)

    if cached_results:

        # VIN in the database, so we query the database and add the output to our cf dictionary
        all_data = c.execute(sql_statements.select, (lookup_VIN,)).fetchall()
        all_data = all_data[0]
        cf = {'VIN': all_data[0], 'Make': all_data[1], 'Model': all_data[2],
              'Model Year': all_data[3], 'Body Class':
                  all_data[4], 'Cached Results': True}
        return cf.items()
    else:

        # VIN not in the database, so we add it to the database and return the results
        # Receiving/cleaning data from the VPIC API, since the information is not stored in the SQL cache
        try:
            url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/" + lookup_VIN + "?format=json"
            r = requests.get(url)
        except requests.exceptions.RequestException as error:
            print(error)
            raise HTTPException(status_code=400, detail="There is an error connecting to the VPIC API")

        # setting the format to json and retrieving only the information we want
        try:
            # Cleaning our data and then adding the data into a dictionary
            data = json.loads(r.text)
            data = data['Results'][0]

            # Making sure the API has been sent a valid VIN
            if len(data['ErrorCode']) > 0 and data['ErrorCode'] != "0":

                err = data['ErrorCode']
                raise HTTPException(status_code=400,
                                    detail="There was no response or an error returned by the API")

            else:
                cf = {'VIN': lookup_VIN, 'Make': data['Make'], 'Model': data['Model'],
                      'Model Year': data['ModelYear'],
                      'Body Class': data['BodyClass'], 'Cached Results': False}
        except Exception as error:
            print(error)
            raise HTTPException(status_code=400, detail="There was no response or an error returned by the API")

        insert_into_db(cf)
        return cf.items()


@app.get("/")
async def root():
    return {"msg": "Welcome to VIN Decoding!"}
