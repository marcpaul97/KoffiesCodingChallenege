create_table = """CREATE TABLE IF NOT EXISTS carFacts(
                        carFactsID integer PRIMARY KEY,
                        VIN text NOT NULL,
                        Make text,
                        Model text,
                        ModelYear text,
                        BodyClass text,
                        CreatedDate text);"""

create_index = """CREATE UNIQUE INDEX IF NOT EXISTS idx_VIN ON carFacts(VIN);"""

insert = """INSERT OR IGNORE INTO carFacts(VIN, Make, Model, ModelYear, BodyClass, CreatedDate) VALUES (?, ?, ?,?,
?, strftime('%m-%d-%Y %H:%M:%S', 'now'));"""

remove = """DELETE FROM carFacts WHERE VIN = ?;"""

check_vin = """SELECT carFactsID FROM carFacts WHERE VIN = ?;"""

get_earliest_created_date = """SELECT carFactsID FROM carFacts WHERE VIN = ? ORDER BY CreatedDate ASC LIMIT 1;"""

select = """SELECT VIN, Make, Model, ModelYear, BodyClass, CreatedDate 'True' FROM carFacts WHERE VIN = ?;"""