from controllers import drivers_controller
from flask import render_template

from flask import jsonify
from flask import Flask
app = Flask(__name__)


@app.route('/drivers')
def all_drivers():
    data = drivers_controller.list_all_drivers()
    data = {
        'drivers': drivers_controller.list_all_drivers()
    }
    return jsonify(data)


@app.route('/drivers/<driver>')
def driver(driver):
    data = drivers_controller.driver_stats(driver)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
