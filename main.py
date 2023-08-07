import urllib.request
import json
import os
import ssl

from flask import Flask, render_template, request

app = Flask(__name__)

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        model = request.form['model']
        year = int(request.form['year'])
        transmission = request.form['transmission']
        mileage = int(request.form['mileage'])
        fuelType = request.form['fuelType']
        tax = float(request.form['tax'])
        mpg = float(request.form['mpg'])
        engineSize = float(request.form['engineSize'])
        make = request.form['make']

        data = {
            "Inputs": {
                "data": [
                    {
                        "model": model,
                        "year": year,
                        "transmission": transmission,
                        "mileage": mileage,
                        "fuelType": fuelType,
                        "tax": tax,
                        "mpg": mpg,
                        "engineSize": engineSize,
                        "Make": make
                    }
                ]
            },
            "GlobalParameters": {}
        }

        # Convert input values to the appropriate data types
        data['Inputs']['data'][0]['year'] = int(data['Inputs']['data'][0]['year'])
        data['Inputs']['data'][0]['mileage'] = int(data['Inputs']['data'][0]['mileage'])
        data['Inputs']['data'][0]['tax'] = float(data['Inputs']['data'][0]['tax'])
        data['Inputs']['data'][0]['mpg'] = float(data['Inputs']['data'][0]['mpg'])
        data['Inputs']['data'][0]['engineSize'] = float(data['Inputs']['data'][0]['engineSize'])

        body = str.encode(json.dumps(data))

        url = 'https://carpricepredictions-wzgpd.centralindia.inference.ml.azure.com/score'
        api_key = '108CxZq6mOVqt4YE22OHNmvxjOqx7cCz'
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key,
            'azureml-model-deployment': 'automldc53aef9431-1'
        }

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            result_json = json.loads(result)
            print(result_json)  # Print the response for inspection

            # Extract the predicted value from the response
            prediction = result_json['Results']

            return render_template('openpage.html', prediction=prediction)

        except urllib.error.HTTPError as error:
            return render_template('openpage.html', error="The request failed with status code: " + str(error.code))

    return render_template('openpage.html')

if __name__ == '__main__':
    app.run(debug=True)