## Project to fetch upcoming launch data with the Launch Library 2 API
# API Documentation can be found here: https://ll.thespacedevs.com/docs/#/

# Import necessary modules
import requests
import psycopg2

# Get URL for all upcoming launches
launch_base_url = 'https://lldev.thespacedevs.com/2.2.0/launch/upcoming/'

# Define a function that will create a URL to fetch the necessary data with the following criteria:
# All upcoming launches need to be included
# They want to go to the moon, so suborbital flights will not work
def fetch_upcoming_launches_URL(limit_input):

    # No suborbital launches since we want to go to the moon
    orbital_filter = 'include_suborbital=false'

    # Limit returned results to just the amount per query
    limit = f"limit={limit_input}"

    # Combine the filters
    filters = '&'.join(
        (orbital_filter, limit)
    )

    # Ordering the results by ascending
    ordering = 'ordering=net'

    # Assemble the query URL
    query_url = launch_base_url + '?' + '&'.join(
        (filters,ordering)
    )

    # Display the URL
    print(query_url)
    # Error handling to see if generated URL is correct
    try:
        response = requests.get(query_url)
        # Check if the response status code is in the range 200-299
        if response.status_code >= 200 and response.status_code < 300:
            print(f"The URL is valid.")
        # Print out message if the URL is not valid
        else:
            print(f"The URL is not valid. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error checking URL {query_url}: {e}")
    return response

# Define a function that will loop through the list of retrieved data and only extract data that has the
# 'LO' abbreviation. This will help filter data to only include launches that will go into Lunar Orbit
def loop_list(data_list):
    # This creates an empty list to store the Lunar Orbit launches
    sorted_list = []
    for i in data_list:
        try:
            result = i.get("mission").get("orbit").get("abbrev") #Get the abbreviation for item in the list
            # Add the retrieved data to the list if the abbreviation is Lunar Orbit (LO)
            if result == 'LO':
                sorted_list.append(i)
        except AttributeError as e:
            # If it is not the correct abbreviation. Pass and continue with the loop
            pass
    return sorted_list

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="password",
    host="localhost",
    port='5432'
)

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create a table for the relevant data to be stored in
create_table_query = '''
CREATE TABLE IF NOT EXISTS launch_table (
    id VARCHAR(100),
    start_window DATE,
    end_window DATE,
    type_launch TEXT,
    launchpad_location TEXT,
    launch_description TEXT
)
'''
cursor.execute(create_table_query)
conn.commit()
print("Table created successfully") #Confirm that the table was created


# First use the function with a limit of 0 to get the amount of results. This is to minimise data called at the start
pre_launch_data = fetch_upcoming_launches_URL(0)

# Save the amount of result to the data_count variable and add 1 to ensure all results will be retrieved
data_count = pre_launch_data.json().get('count') + 1

# Now use the data_count variable for the limit to retrieve all the data
launch_data = fetch_upcoming_launches_URL(data_count)

# Save the upcoming launches data that was retrieved to a variable
launch_data_results = launch_data.json().get('results')

# Use the obtained results in the loop_list function to only get the lunar orbit launches
final_results = loop_list(launch_data_results)

# Loop through the final filtered list and insert all the relevant variables and insert into the table and commit to
# the docker postgres database
for i in final_results:
    id = i.get('id')
    window_start = i.get('window_start')
    window_end = i.get('window_end')
    type = i.get('type')
    location = i.get('pad').get('location').get('name')
    description = i.get('mission').get('description')

    # Using parameterized query to insert data into the database
    cursor.execute('''INSERT INTO launch_table (id, start_window, end_window, type_launch, launchpad_location, 
    launch_description) VALUES (%s, %s, %s, %s, %s, %s)''', (id, window_start, window_end, type, location, description))
    conn.commit()

cursor.close()
conn.close()