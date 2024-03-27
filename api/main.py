import os
from flask import Flask, request
import utils
# import postgre_create as create_utils
import logging
# import datetime
# import requests
# import json
# import time

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

postgre = None

@app.route("/api/echo", methods=["GET"])
def echo():
    return "Hello Postgres!"

if __name__ == "__main__":
    app.logger.info("Connecting to postgres")
    postgre = utils.get_postgre()
    app.logger.info("Connected to postgres")

    # if is_scheme_created(postgre):
    #     app.logger.info("Scheme already created. Simple start")
    # else:
        # prepare_database(postgre)

    app.run(host="0.0.0.0", port=os.environ["LOCAL_SERVICES_PORT"])