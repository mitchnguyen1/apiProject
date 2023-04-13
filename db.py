from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

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

#run on port 8080
if __name__ == '__main__':
    app.run(port=8080)
