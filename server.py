from flask import Flask, request, Response, send_file
from redis import Redis
from rq import Queue
import json

from process import process_images

INPUT_DIR = 'upload_images/input/'
STYLE_DIR = 'upload_images/style/'

FINAL_RESULT_DIR = 'images/final_results/'

app = Flask(__name__)
q = Queue(connection=Redis(), default_timeout=3600)

index_count = 1


@app.route('/process', methods=['POST'])
def receive_order():
    input_img = request.files['input']
    style_img = request.files['style']
    global index_count  # TODO: make unique index validation
    input_img.save(INPUT_DIR + 'in' + str(index_count) + '.png')
    style_img.save(STYLE_DIR + 'tar' + str(index_count) + '.png')

    r = q.enqueue(process_images, index_count, result_ttl=86400)
    index_count += 1

    return Response(r.id, status=201)


@app.route('/result/<order_id>', methods=['GET'])
def return_result(order_id):
    try:
        job = q.fetch_job(order_id)
        # if job.is_finished:
        #     return json.dumps(job.status, ensure_ascii=False)
        # else:
        #     # return Response('Not Ready', status=202)
        #     return json.dumps(job.status, ensure_ascii=False)
        index = job.args[0]
        if job.is_finished:
            return send_file(FINAL_RESULT_DIR + 'best' + str(index) + '_t_1000.png', as_attachment=True)
        else:
            return Response(job.status, status=202)

    except Exception:
        return Response('Not Found', status=404)
