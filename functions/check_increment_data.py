import sys
import traceback
import pandas as pd
from datetime import datetime
from functions import log
from config import fema_config
from sqlalchemy import create_engine
from functions import  get_data_count_database, log, send_mail, insert_excel_data_to_mysql
from sqlalchemy.sql import text
from config import fema_config



def check_increment_data(excel_path):
    print("check_increment_data function is called")




    try:
        # database_uri = f'mysql://{fema_config.user}:{fema_config.password}@{fema_config.host}/{fema_config.database}?auth_plugin={fema_config.auth_plugin}'
       
        # # Directly define the database URI
        
        # # database_uri = f'mysql://{fema_config.user}:{fema_config.password}@{fema_config.host}/{fema_config.database}'
        # engine = create_engine(database_uri)
        query = "SELECT * FROM rbi_fema_python"
       
        with fema_config.db_connection() as connection:
            database_df = pd.read_sql(query, con=connection)

    

        missing_rows_in_db = []
        missing_rows_in_excel = []

        
        try:
            # # Connect to the database
            # with fema_config.db_connection() as connection:
            #     query = "SELECT * FROM rbi_fema"
            #     database_df = pd.read_sql(query, con=connection)

            # engine = get_db_engine()
            # query = "SELECT * FROM rbi_fema"
            # database_df = pd.read_sql(query, con=engine)

            # Read Excel file
            excel_df = pd.read_excel(excel_path)

            # Ensure consistent types and formats
            database_df["name_of_applicant"] = database_df["name_of_applicant"].astype(str).str.strip()
            excel_df["name_of_applicant"] = excel_df["name_of_applicant"].astype(str).str.strip()

            database_df["details_of_contraventions"] = database_df["details_of_contraventions"].astype(str).str.strip()
            excel_df["details_of_contraventions"] = excel_df["details_of_contraventions"].astype(str).str.strip()

            # database_df["date_of_order"] = pd.to_datetime(database_df["date_of_order"], errors='coerce').dt.date
            # excel_df["date_of_order"] = pd.to_datetime(excel_df["date_of_order"], errors='coerce').dt.date

            database_df["amount_imposed"] = database_df["amount_imposed"].astype(str).str.strip()
            excel_df["amount_imposed"] = excel_df["amount_imposed"].astype(str).str.strip()

            # Check missing rows in Excel
            missing_rows_in_excel = []
            for index, row in database_df.iterrows():
                if not (
                    row["name_of_applicant"] in excel_df["name_of_applicant"].values and
                    row["details_of_contraventions"] in excel_df["details_of_contraventions"].values and
                    # row["date_of_order"] in excel_df["date_of_order"].values and
                    row["amount_imposed"] in excel_df["amount_imposed"].values
                ):
                    missing_rows_in_excel.append(row)

            # Check missing rows in Database
            missing_rows_in_db = []
            for index, row in excel_df.iterrows():
                if not (
                    row["name_of_applicant"] in database_df["name_of_applicant"].values and
                    row["details_of_contraventions"] in database_df["details_of_contraventions"].values and
                    # row["date_of_order"] in database_df["date_of_order"].values and
                    row["amount_imposed"] in database_df["amount_imposed"].values
                ):
                    missing_rows_in_db.append(row)
        except:
            pass


        for row in missing_rows_in_excel:
            # print(missing_rows_in_excel)
            fema_config.deleted_sources += row["name_of_applicant"] + ", "

        # Convert missing_rows_in_excel to a DataFrame
        missing_rows_in_excel_df = pd.DataFrame(missing_rows_in_excel)


        # Update the flag column for the deleted sources in database as deleted
        # for index, row in missing_rows_in_excel_df.iterrows():
        #     order_link = row['order_link']
        #     update_query = f"""
        #         UPDATE fema_orders_section43a_44
        #         SET flag = 'deleted'
        #         WHERE order_link = '{order_link}'
        #     """
        #     cursor.execute(update_query)
        #     fema_config.connection.commit()
        # print("deleted sources pdf in excel", fema_config.deleted_sources)
        updated_rows_in_db = []
        updated_rows_in_excel = []

        
        print(len(missing_rows_in_db), "missing rows in database")
        print(len(missing_rows_in_excel), "missing rows in Excel")
        # print(missing_rows_in_db,"missing rows in db")
        fema_config.no_data_avaliable = len(missing_rows_in_db)
        fema_config.no_data_scraped = len(missing_rows_in_db)
        fema_config.deleted_source_count = len(missing_rows_in_excel)

        if len(missing_rows_in_excel) > 0 and len(missing_rows_in_db) == 0:
            fema_config.log_list[1] = "Success"
            fema_config.log_list[4] = get_data_count_database.get_data_count_database()
            # fema_config.log_list[6] = f"{update_db}, Some data are deleted in the website"

            fema_config.log_list[6] = f"Some data are deleted in the website"
            log.insert_log_into_table(fema_config.log_list)
            print("log table====", fema_config.log_list)
            fema_config.log_list = [None] * 8
            sys.exit()

        elif len(missing_rows_in_db) == 0:
            fema_config.log_list[1] = "Success"
            fema_config.log_list[4] = get_data_count_database.get_data_count_database()
            # fema_config.log_list[6] = f"{update_db}, no new data"
            
            fema_config.log_list[6] = f"no new data"

            fema_config.log_list[6] = f"no new data"
            log.insert_log_into_table(fema_config.log_list)
            print("log table====", fema_config.log_list)
            fema_config.log_list = [None] * 8
            sys.exit()

        current_date = datetime.now().strftime("%Y-%m-%d")
        increment_file_name = f"incremental_excel_sheet_{current_date}.xlsx"
        increment_data_excel_path = fr"C:\Users\Premkumar.8265\Desktop\rbi_fema\data\incremental_excel_sheet\{increment_file_name}"
        
        # missing_rows_in_db.to_excel(increment_data_excel_path, index=False)
        pd.DataFrame(missing_rows_in_db).to_excel(increment_data_excel_path, index=False)
        insert_excel_data_to_mysql.insert_excel_data_to_mysql(increment_data_excel_path)
    except Exception as e:
        traceback.print_exc()
        fema_config.log_list[1] = "Failure"
        fema_config.log_list[4] = get_data_count_database.get_data_count_database()
        fema_config.log_list[5] = "error in checking in incremental part"
        log.insert_log_into_table(fema_config.log_list)
        print("checking incremental part error:", fema_config.log_list)
        send_mail.send_email("fema section checking incremental part error", e)
        fema_config.log_list = [None] * 8
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error occurred at line {exc_tb.tb_lineno}:")
        print(f"Exception Type: {exc_type}")
        print(f"Exception Object: {exc_obj}")
        print(f"Traceback: {exc_tb}")
        sys.exit()
