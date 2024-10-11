#导入flask
from flask import Flask
from flask import request
import thread
import logging

import sets
import keys

app = Flask(__name__)
@app.route('/',methods=['POST'])
def index():
    data = request.get_json()
    print(data)

    return {}
@app.route('/hello',methods=['GET'])
def test():
    print('hello')
    return 'hello world'



if __name__ == '__main__':
    app.run(port=8086,host='0.0.0.0')