from flask import Flask, request, render_template, jsonify
from urllib.parse import urlparse
import ipaddress
import joblib
import os

app = Flask(__name__)

try:
    model = joblib.load('model.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

    


# URL Feature Extraction Functions

def getDomain(url):
    sanitized_url = url.replace('[.]', '.')
    domain = urlparse(sanitized_url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def havingIP(url):
    try:
        ipaddress.ip_address(url)
        return 1
    except ValueError:
        return 0


def haveAtSign(url):
    return 1 if "@" in url else 0


def getLength(url):
    return 0 if len(url) < 54 else 1


def getDepth(url):
    path_segments = urlparse(url).path.split('/')
    depth = sum(1 for segment in path_segments if segment)
    return depth


def redirection(url):
    return 1 if '//' in urlparse(url).path else 0


def httpDomain(url):
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else 0


def tinyURL(url):
    shortening_services = ["bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "t.co", "is.gd", "buff.ly", "adf.ly", "bit.do"]
    domain = urlparse(url).netloc
    return 1 if any(service in domain for service in shortening_services) else 0


def prefixSuffix(url):
    domain = urlparse(url).netloc
    return 1 if '-' in domain else 0


def featureExtraction(url):
    features = [
        havingIP(url),
        haveAtSign(url),
        getLength(url),
        getDepth(url),
        redirection(url),
        httpDomain(url),
        tinyURL(url),
        prefixSuffix(url)
    ]
    return features


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}"

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form.get('url')  # Retrieve the URL from the form
    features = featureExtraction(url)  # Extract features from the URL

    # Use the model to make a prediction
    prediction = model.predict([features])[0]

    # Interpret prediction (1 = phishing, 0 = legitimate)
    result = "Phishing" if prediction == 1 else "Legitimate"

    # Render the template and pass the prediction result
    return render_template('index.html', prediction_text=result)



if __name__ == '__main__':
    app.run(debug=True)
