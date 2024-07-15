from datetime import datetime
import json
import os
import threading

from flask import request, Response
from flask_restful import Resource, output_json
from werkzeug.utils import secure_filename
from app.api.backend import gpt_querier
import app.shared as shared


class Upload(Resource):
    """
    This class is a resource for the API endpoint /upload. In the request, the user can upload a file with answers and
    the actual question. The file is then processed by the GPT API and the results are stored in a file.
    """
    def post(self):
        """
        This method handles the POST request to the endpoint /upload.
        :return: an acknowledgement that the file was uploaded and a time-based task id to identify the  file on the
        server
        """
        try:
            task_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            metadata = request.files['metadata'].read().decode('utf-8')
            json_data = json.loads(metadata)

            file = request.files['file']
            filename = secure_filename(file.filename).split('.')[0]
            answers = convert_file_content_into_list(file)

            shared.tasks[task_id] = {"status": "processing", "progress": f" 0 of {len(answers)}"}
            thread = threading.Thread(target=gpt_querier.query_run,
                                      args=(task_id, filename, json_data, answers))
            thread.start()
            result = {"status": "file uploaded", "taskId": f"{task_id}"}
            response = output_json(result, 200)
            response.headers['Content-Type'] = 'application/json'

            return response
        except Exception as e:
            return output_json(f"Error: {e}", 500)


class Download(Resource):
    """
    This class is a resource for the API endpoint /download. In the request, the user can download the file with the
    file if it is ready to be downloaded. If an error occurred during the processing, the user will receive an error
    message.
    """
    def get(self, task_id):
        """
        This method handles the GET request to the endpoint /download.
        :param task_id: the task id to identify the file to be downloaded
        :return: the processing status of the file | the file to be downloaded | an error message 500 or 404
        """
        task = shared.tasks[task_id]
        status = task["status"]
        if status == "processing":
            progress = task["progress"]
            result = {"status": "processing", "progress": f"{progress}"}
            response = output_json(result, 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        if status == "Done":
            file_name = task["fileName"]
            try:
                # create a Response object and with Response 200
                with open(f"app/{task_id}.txt", 'r') as file:
                    # safe content into a temporary file
                    file_content = file.read()
                # delete the file from the server
                os.remove(f"app/{task_id}.txt")
                response = Response(file_content, mimetype='application/octet-stream')
                response.headers.set('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
                response.status = 200

                return response
            except FileNotFoundError as e:
                print(e)
                return "File not Found", 404
        if status == "Error":
            progress = task["progress"]
            if os.path.exists(f"app/{task_id}.txt"):
                os.remove(f"app/{task_id}.txt")
            result = {"status": "Error", "progress": f"{progress}"}
            response = output_json(result, 500)
            response.headers['Content-Type'] = 'application/json'
            return response


def convert_file_content_into_list(file):
    """
    Method to convert the file content into a list. It uses as default the separator symbol '###' and only works with
    this separator
    :param file: the file to be converted containing the answers
    :return: list of answers
    """
    # read file content
    inhalt = file.read().decode('utf-8')

    # split answers with the separater symbol
    antworten_roh = inhalt.split('###')

    # safe every answer in list
    antworten = [antwort.strip() for antwort in antworten_roh if antwort.strip()]
    return antworten
