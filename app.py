from scraper import driver_data

from flask import jsonify
from flask import Flask
app = Flask(__name__)
# print(scraper)


@app.route('/')
def all_drivers():
    print(driver_data.driver_stats("lewis-hamilton"))
    return 'Hello, World!'

# # individual driver data
# @app.route('/racing/api/v0.1/drivers/<driver>')
# def drivers_data(driver):
#     return driver


if __name__ == '__main__':
    app.run(debug=True)
