from kafka import KafkaConsumer
import threading
# 使用group,對於同一個group的成員只有一個消費者例項可以讀取資料

def consume():
    while True:
        consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'])
        consumer.subscribe(topics=('test2'))  #訂閱要消費的主題
        for message in consumer:
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key,message.value))

       
t = threading.Thread(target = consume)
t.start()

for i in range(2):
    print("我是主要程式碼", i)
    time.sleep(1)

