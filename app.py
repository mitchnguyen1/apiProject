import re
import requests
import psycopg2
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS


# Connect to the database
conn = psycopg2.connect(database="song_4eid", user="mitch", password="lOhQzEazORh9ISV2WWHNbORJtbYDOX3m", host="dpg-cgqsoiu4dadbdtfd2ir0-a.ohio-postgres.render.com", port="5432")
cur = conn.cursor()

# Truncate the table
cur.execute("TRUNCATE TABLE GHM")

# Fetch data from the website
url = 'https://greenheartmeals.com/currentmenu/?dd=2023-04-15'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

buttons = soup.find_all('button', class_='new_button_square_small')
menu_title = soup.find_all('p', {'class': 'menu_title'})
menu_descr = soup.find_all('p', {'class': 'menu_description'})
menu_imgs = soup.find_all('div', {'class': 'col-sm-4 col-xs-4 p-0'})

menu_items = []

# Extract data from the website and insert into the database
for button, title, descr, div in zip(buttons, menu_title, menu_descr, menu_imgs):
    onclick = button.get('onclick')
    img_tag = div.find('img', src=True)
    match = re.search(r'openModalMealsByUnit\((\d+),\s*\'(\d{4}-\d{2}-\d{2})\'\)', onclick)
    if match:
        img_url = img_tag['src']
        id, dd = match.groups()
        menu_items.append({
            'title': title.text.strip(),
            'id': id,
            'dd': dd,
            'img_url': img_url,
            'description': descr.text.strip()
        })
        # Insert data into the database
        cur.execute("INSERT INTO GHM (title, id, dd, img_url, description) VALUES (%s, %s, %s, %s, %s)", (title.text.strip(), id, dd, img_url, descr.text.strip()))

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()


app = Flask(__name__)
CORS(app)


@app.route('/ghm')
def get_ghm_menu():
    # Connect to the database
    conn = psycopg2.connect(
        host="dpg-cgqsoiu4dadbdtfd2ir0-a.ohio-postgres.render.com",
        database="song_4eid",
        user="mitch",
        password="lOhQzEazORh9ISV2WWHNbORJtbYDOX3m"
    )

    # Create a cursor object
    cur = conn.cursor()

    # Execute a SQL query
    cur.execute("SELECT * FROM GHM")

    # Fetch the results
    results = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Convert the results to a list of dictionaries
    menu_items = []
    for result in results:
        menu_item = {
            'title': result[0],
            'id': result[1],
            'dd': result[2],
            'img_url': result[3],
            'description': result[4]
        }
        menu_items.append(menu_item)

    # Return the menu data as a JSON response
    response = jsonify(menu_items)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(port=8080)
