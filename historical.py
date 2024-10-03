import time
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import fema_config

def scrape_rbi_data():
    # Setup WebDriver
    browser = webdriver.Chrome()
    # URL to scrape
    url = "https://www.rbi.org.in/scripts/SummaryCompoundingorders.aspx"
    browser.get(url)
    browser.maximize_window()
    # Wait for the table to load
    wait = WebDriverWait(browser, 20)
    table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tablebg")))
    # Extract table data
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows[1:]:  # Skip the header row
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = [col.text for col in cols[1:]]  # Skip the first column (Sr.No)
        data.append(row_data)
    
    # Create a pandas DataFrame
    df = pd.DataFrame(data, columns=["name_of_applicant", "details_of_contraventions", "date_of_order", "amount_imposed"])
    # Save to Excel
    excel_file = "rbi_compounding_orders.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Data has been saved to {excel_file}")
    # Close the browser
    browser.quit()
    return excel_file

def read_excel_and_insert_to_mysql(excel_file):
    print("read_excel_and_insert_to_mysql is called")
    # Read data from Excel
    df = pd.read_excel(excel_file)
    
    # Connect to MySQL
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='rbi'
    )
    cursor = connection.cursor()
    
    # SQL insert query
    insert_query = """
    INSERT INTO rbi_fema (name_of_applicant, details_of_contraventions, date_of_order, amount_imposed, scraped_at)
    VALUES (%s, %s, %s, %s, NOW())
    """
    
    # Insert data into MySQL table
    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row['name_of_applicant'],
            row['details_of_contraventions'],
            pd.to_datetime(row['date_of_order'], errors='coerce').date(),  # Convert to date format
            row['amount_imposed']
        ))
    
    # Commit the transaction
    connection.commit()
    
    # Close the database connection
    cursor.close()
    connection.close()
    print("Data has been successfully inserted into the MySQL database.")

if __name__ == "__main__":
    # Step 1: Scrape data and save to Excel
    excel_file = scrape_rbi_data()
        
    first_excel_sheet_name =f"first_excel_sheet_{fema_config.current_date}.xlsx"
    first_exceL_sheet_path = rf"C:\Users\Premkumar.8265\Desktop\rbi_fema\data\first_excel_sheet\{first_excel_sheet_name}"
    # Step 2: Read from Excel and insert data into MySQL
    read_excel_and_insert_to_mysql(first_exceL_sheet_path)
