import sys
import traceback
import pandas as pd
import mysql.connector
from config import fema_config
from functions import get_data_count_database, send_mail, log


def insert_excel_data_to_mysql(excel_file):
    print("insert_excel_data_to_mysql function is called")

    connection = fema_config.db_connection()
    cursor = connection.cursor()

    try:
        # Read data from Excel
        df = pd.read_excel(excel_file)

        # SQL insert query
        insert_query = """
        INSERT INTO rbi_fema_python(name_of_applicant, details_of_contraventions, date_of_order, amount_imposed, scraped_at)
        VALUES (%s, %s, %s, %s, NOW())
        """

        # Insert data into MySQL table
        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['name_of_applicant'],
                row['details_of_contraventions'],
                # pd.to_datetime(row['date_of_order'], errors='coerce').date(),  # Convert to date format
                pd.to_datetime(row['date_of_order'], format='%d-%m-%Y', errors='coerce').date(),
                row['amount_imposed']
            ))

        # Commit the transaction
        connection.commit()

        fema_config.log_list[1] = "Success"
        fema_config.log_list[2] = fema_config.no_data_avaliable
        fema_config.log_list[3] = fema_config.no_data_scraped
        fema_config.log_list[4] = get_data_count_database.get_data_count_database()
        fema_config.log_list[6] = f"{fema_config.updated_count} rows updated"
        print("log table====", fema_config.log_list)
        log.insert_log_into_table(fema_config.log_list)
        fema_config.log_list = [None] * 8
        print("Data has been successfully inserted into the MySQL database.")
        sys.exit()
    except Exception as e:
        fema_config.log_list[1] = "Failure"
        fema_config.log_list[4] = get_data_count_database.get_data_count_database()
        fema_config.log_list[5] = "error in insert part"
        print("log table====", fema_config.log_list)
        log.insert_log_into_table(fema_config.log_list)
        
        fema_config.log_list = [None] * 8
        traceback.print_exc()
        send_mail.send_email("fema section Data inserted into the database error", e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error occurred at line {exc_tb.tb_lineno}:")
        print(f"Exception Type: {exc_type}")
        print(f"Exception Object: {exc_obj}")
        print(f"Traceback: {exc_tb}")
        sys.exit("script error")







