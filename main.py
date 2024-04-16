import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import pymysql

# Directory path
connection_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'oussama',
    'port': 3306
}


def treat_data(file_path):
    flag = False
    valuesX = []
    valuesY = []
    date=""
    wa=""
    flag_write = False

    with open(file_path, 'r') as fileToTreat:
        lines = fileToTreat.readlines()

        x = ""
        y = ""


        for i, line in enumerate(lines, start=1):
            valuesY=[]
            valuesY.extend([str(val) for val in line.strip().split()])
            if i == 1:
                date = line.strip().split(":")[1]
            if i == 2:
                wa = line.strip().split(":")[1]

            if flag:
                valuesX.extend([str(val) for val in line.strip().split()])
                flag = False
                flag_write = True
               # print(valuesX)
            if line.strip() == "Messdaten:":
                flag = True
        print(len(valuesX))
        print(len(valuesY))
        if flag_write:

            try:
                connection = pymysql.connect(**connection_config)
                print("Connected to MySQL database")
                cursor = connection.cursor()

                create_table_query = """
                    CREATE TABLE IF NOT EXISTS your_table3 (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        x varchar(255),
                        y varchar(255),
                        wa varchar(255),
                        datum varchar(255)
                    )
                """
                cursor.execute(create_table_query)
                print("Table created successfully or already exists")

                data_to_insert = [( x, y, wa, date) for x, y in zip(valuesX, valuesY)]
                # SQL query to insert data1.txt into the table
                insert_query = """
                    INSERT INTO your_table3 (x, y,wa, datum)
                    VALUES ( %s, %s,%s,%s)
                """
                # Execute the SQL query for each data1.txt row
                cursor.executemany(insert_query, data_to_insert)
                connection.commit()
                print("Data inserted successfully to your_table")

                ###############################################################################

            except pymysql.Error as e:
                print(f"Error connecting to MySQL database: {e}")
            finally:
                # Close cursor and connection
                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals() and connection.open:
                    connection.close()
            valuesX = []
            valuesY = []
            flag_write = False


    # Database connection details


class MyHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        super().__init__()
        self.log_file = log_file

    def log_event(self, event_type, file_path):
        with open(self.log_file, 'a') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            username = os.getenv('USER') or os.getenv('USERNAME')  # Get current user
            f.write(f"{timestamp} - {username} - {event_type}: {file_path}\n")

    def on_any_event(self, event):
        if event.is_directory:
            return  # Ignore directory events

        if event.event_type == 'created':

            self.log_event('Created', event.src_path)
            treat_data(event.src_path)
        elif event.event_type == 'deleted':

            self.log_event('Deleted', event.src_path)


# Function to start the observer
def start_observer(directory, log_file):
    event_handler = MyHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    print(f"Watching directory: {directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Directory to monitor
directory_to_monitor = "my_folder"

# Log file
log_file = "log.txt"

# Start monitoring the directory
start_observer(directory_to_monitor, log_file)
