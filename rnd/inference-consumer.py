from kafka import KafkaConsumer, KafkaProducer
import os
import json
import numpy as np
import dlib
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import statistics

TOPIC_NAME = "input"
TOPIC2_NAME = "output"


KAFKA_SERVER = "localhost:29092"


consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_SERVER,
    # to deserialize kafka.producer.object into dict
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER
)


def inferencProcessFunction(data):

    result_data = data
    producer.send(TOPIC2_NAME, result_data)


for inf in consumer:
    inf_data = inf.value
    print("get data: ", inf_data)
    inferencProcessFunction(inf_data)