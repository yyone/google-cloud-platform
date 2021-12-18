import logging
from flask import Flask, abort, url_for, request, render_template
from forms import MyForm
from google.cloud import logging as cloud_logging
from google.cloud import datastore, storage, tasks_v2
import ds

logging_client = cloud_logging.Client() # ロギングオブジェクト取得
logging_client.setup_logging() # Python loggingと結びつける
logger = logging.getLogger("MyExampleApplication") # ロガー取得
logger.setLevel(logging.DEBUG) # 出力レベルをセット

app = Flask(__name__)

app.config.update(dict(
  SECRET_KEY="powerful secretkey",
  WTF_CSRF_SECRET_KEY="a csrf secret key"
))


@app.route("/", methods=["GET", "POST"])
def home():
  ## Cloud Tasks用設定
  # # Taskクライアントを取得
  # client = tasks_v2.CloudTasksClient()

  # # プロジェクトID、ロケーション、キューID
  # project = "abiding-base-335400"
  # location = "asia-northeast1"
  # queue_id = "my-queue"

  # # タスクを処理するAppEngineタスクハンドラ
  # relative_uri = url_for("run_task")

  # # タスクの作成
  # task = {
  #   "app_engine_http_request": {
  #     "http_method": "POST",
  #     "relative_uri": relative_uri,
  #     "body": "Hello Cloud Tasks!".encode(),
  #   }
  # }

  # # 完全修飾のキーの名前を作成
  # parent = client.queue_path(project, location, queue_id)

  # # タスクをキューに追加する
  # task_response = client.create_task(request={"parent": parent, "task": task})
  # logging.info("Task {} がキューに追加されました".format(task_response.name))

  # 通常処理
  message = ""
  form = MyForm(csrf_enabled=False)
  if form.validate_on_submit():
    message = form.message.data
  else:
    message_validation_errors = form.errors.get("message")
    if message_validation_errors:
      message = message_validation_errors[0] # 今回は0番目のエラーのみ表示する
  
  return render_template(
    "index.html",
    message=message,
    form=form
  )


@app.route("/api/greetings/<key_id>", methods=["GET", "PUT", "DELETE"])
@app.route("/api/greetings", methods=["GET", "POST"])
def greetings(key_id=None):
  if request.method == "GET":
    if key_id:
      entity = ds.get_by_id(key_id)
      if not entity:
        abort(404)
      return entity
    else:
      greetings = ds.get_all()
      res = {
        "greetings": greetings
      }
      return res
  elif request.method == "POST":
    author = request.json["author"]
    message = request.json["message"]
    entity = ds.insert(author, message)
    return entity, 201
  elif request.method == "PUT":
    entity = ds.get_by_id(key_id)
    if not entity:
      abort(404)
      return entity
    
    entity["author"] = request.json["author"]
    entity["message"] = request.json["message"]
    entity = ds.update(entity)
    return entity
  elif request.method == "DELETE":
    ds.delete(key_id)
    return "", 204


@app.route("/api/comments", methods=["GET", "POST"])
def comments():
  if request.method == "GET":
    parent_id = request.args.get("parent_id")
    entities = ds.get_comments(parent_id)
    res = {
      "comments": entities
    }
    return res, 200
  elif request.method == "POST":
    parent_id = request.json["parent_id"]
    message = request.json["message"]
    entity = ds.insert_comment(parent_id, message)
    return entity, 201


@app.route("/photos", methods=["GET", "POST"])
def photos():
  if request.method == "GET":
    client = storage.Client()
    bucket = client.get_bucket("abiding-base-335400")
    return render_template("photos.html", blobs=bucket.list_blobs())
  else:
    uploaded_file = request.files["file"]
    client = storage.Client()
    bucket = client.get_bucket("abiding-base-335400")
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_file(uploaded_file)
    return render_template("complete.html")


@app.route("/run_task", methods=["POST"])
def run_task():
  logging.info("running!!!")
  payload = request.get_data(as_text=True)
  logging.info("payload={}".format(payload))
  return "", 200


@app.route("/run_job", methods=["POST"])
def run_job():
  logging.info("Running Scheduler!!!")
  payload = request.get_data(as_text=True)
  logging.info("payload={}".format(payload))
  return "", 200


@app.route("/err500")
def err500():
  abort(500)


@app.errorhandler(404)
def error_404(exception):
  # logging.exception(exception)
  return {"message": "Error: Resource not Found."}, 404


@app.errorhandler(500)
def error_500(exception):
  # logging.exception(exception)
  return {"message": "Please contact the administrator."}, 500


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=8080, debug=True)
