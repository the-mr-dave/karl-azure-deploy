from datetime import datetime
import json
import os
import threading
from tempfile import NamedTemporaryFile

from flask import request, send_file
from flask_restful import Resource, output_json
from werkzeug.utils import secure_filename
from app.api.backend import gpt_querier
import app.shared as shared


class Upload(Resource):
    def post(self):
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


class Download(Resource):
    def get(self, task_id):
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
            print(file_name)
            try:
                with open(f"{task_id}.txt", 'r') as file:
                    file_content = file.read()

                    # Erstellen eines temporären Dateiobjekts
                    temp_file = NamedTemporaryFile(delete=False)
                    temp_file.write(file_content.encode('utf-8'))
                    temp_file.seek(0)

                    # Senden der Datei
                    response = send_file(temp_file.name, as_attachment=True, download_name=file_name)

                    # Schließen und Löschen der temporären Datei
                    temp_file.close()

                    return response
            except FileNotFoundError:
                return "File not Found", 404
        if status == "Error":
            progress = task["progress"]
            if os.path.exists(f"{task_id}.txt"):
                os.remove(f"{task_id}.txt")
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
