from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import sqlite3 as sql
from kafka import KafkaConsumer, KafkaProducer

con = sql.connect('app.db')

app = Flask(__name__)
TOPIC_NAME = "input"
TOPIC2_NAME = "output"

KAFKA_SERVER = "localhost:29092"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    api_version=(0, 11, 15)
)

consumer = KafkaConsumer(
    TOPIC2_NAME,
    bootstrap_servers=KAFKA_SERVER,
    # to deserialize kafka.producer.object into dict
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
)

@app.route('/predict', methods=['POST'])
def kafkaProducer():
    req = request.get_json()
    json_payload = json.dumps(req)
    resp = json.loads(json_payload)
    json_payload = str.encode(json_payload)
    # push data into INFERENCE TOPIC
    producer.send(TOPIC_NAME, json_payload)
    producer.flush()
    print()
    print("Sent to consumer")
    return jsonify({
        "message": "You will receive an email in a short while with the plot",
        "status": "Pass"})

def processResultMessage(data):
    print('Recieved: ', data)
    try:
        url = request.form['url']
        predict = request.form['predict']
        time = request.form['time']

        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO requests (URL,PREDICTION, ELAPSED_TIME) VALUES(?, ?, ?)",(url,predict,time) )
            con.commit()
            msg = "Record successfully added"
    except:
        con.rollback()
        msg = "error in insert operation"



for inf in consumer:
    inf_data = inf.value
    print("get data: ", inf_data)
    processResultMessage(inf_data)



if __name__ == "__main__":
    app.run(debug=True, port=5000)