from flask import Flask, request, Response
from redis import Redis
from rq import Queue
import json

from process import process_images

INPUT_DIR = 'upload_images/input/'
STYLE_DIR = 'upload_images/style/'

app = Flask(__name__)
q = Queue(connection=Redis(), default_timeout=3600)

index_count = 1


@app.route('/process', methods=['POST'])
def receive_order():
    input_img = request.files['input']
    style_img = request.files['style']
    global index_count  # TODO: make unique index validation
    input_img.save(INPUT_DIR+'input'+str(index_count)+'.png')
    style_img.save(STYLE_DIR+'style'+str(index_count)+'.png')
    index_count += 1

    r = q.enqueue(process_images, 1)

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
        return json.dumps(job.status, ensure_ascii=False)

    except Exception:
        return Response('Not Found', status=404)
