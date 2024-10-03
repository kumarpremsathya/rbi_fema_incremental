import time
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from config import fema_config
from functions import log, get_data_count_database, check_increment_data, send_mail
import sys
import traceback


def extract_all_data_in_website():

    try:
        try:
            # Setup WebDriver
            browser = webdriver.Chrome()
            # URL to scrape
            url = "https://www.rbi.org.in/scripts/SummaryCompoundingorders.aspx"
            browser.get(url)
            browser.maximize_window()
            # Wait for the table to load
            wait = WebDriverWait(browser, 20)
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tablebg")))

        except (TimeoutException, WebDriverException, NoSuchElementException) as e:
            raise Exception("Website not opened correctly") from e
        
        # Extract table data
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows[1:]:  # Skip the header row
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = [col.text for col in cols[1:]]  # Skip the first column (Sr.No)
            data.append(row_data)
        
        # Create a pandas DataFrame
        df = pd.DataFrame(data, columns=["name_of_applicant", "details_of_contraventions", "date_of_order", "amount_imposed"])

        first_excel_sheet_name = f"first_excel_sheet_{fema_config.current_date}.xlsx"
        
        first_exceL_sheet_path = rf"C:\Users\Premkumar.8265\Desktop\rbi_fema\data\first_excel_sheet\{first_excel_sheet_name}"

        df.to_excel(first_exceL_sheet_path, index=False)

        print(f"Data has been saved to {first_excel_sheet_name}")
        # print("df========\n\n", df.to_string( ))
        check_increment_data.check_increment_data(first_exceL_sheet_path)
  
    except Exception as e:
        fema_config.log_list[1] = "Failure"
        fema_config.log_list[4] = get_data_count_database.get_data_count_database()

        if str(e) == "Website not opened correctly":
            fema_config.log_list[5] = "Website is not opened"
        else:
            fema_config.log_list[5] = "Error in data extraction part"
        
        print("error in data extraction part======", fema_config.log_list)
        log.insert_log_into_table(fema_config.log_list)
        fema_config.log_list = [None] * 8
        traceback.print_exc()
        send_mail.send_email("fema section extract data in website error", e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error occurred at line {exc_tb.tb_lineno}:")
        print(f"Exception Type: {exc_type}")
        print(f"Exception Object: {exc_obj}")
        print(f"Traceback: {exc_tb}")
        sys.exit("script error")