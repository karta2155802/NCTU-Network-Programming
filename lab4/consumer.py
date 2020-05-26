from kafka import KafkaConsumer
import threading
import time
# 使用group,對於同一個group的成員只有一個消費者例項可以讀取資料

def consume():
    while True:
        for message in consumer:
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key,message.value))

consumer = KafkaConsumer(group_id = 'A', bootstrap_servers=['127.0.0.1:9092'])
consumer.subscribe(topics=('test','test2'))
consumer.subscribe(topics=('test'))
t = threading.Thread(target = consume)
t.start()



