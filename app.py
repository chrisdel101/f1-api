from flask import Flask
app = Flask(__name__)

app.run(debug=True)


@app.route('/')
def test():
    return 'Hello, World!'

# individual driver data
@app.route('/racing/api/v0.1/drivers/<driver>')
def drivers_data(driver):
    return driver


if __name__ == '__main__':
    app.run()
