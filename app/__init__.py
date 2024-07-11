from flask import Flask, render_template, g
from flask_restful import Api
from multiprocessing import Manager
from flask_cors import CORS
import app.shared as shared


from app.api.gpt_endpoint import Upload, Download

app = Flask(__name__)
CORS(app, expose_headers=['Content-Disposition'])
api = Api(app, prefix='/api')


api.add_resource(Upload, '/upload')
api.add_resource(Download, '/download/<task_id>')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    shared.init_global_variable()
    app.run()
