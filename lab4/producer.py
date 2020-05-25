from kafka import KafkaProducer
import time
producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])  #此處ip可以是多個['0.0.0.1:9092','0.0.0.2:9092','0.0.0.3:9092' ]


i=0
while True:
    i+=1
    msg = "producer1+%d" % i
    print(msg)
    producer.send('test', msg.encode('utf-8'))  # 引數為主題和bytes資料
    #producer.send('test2', msg.encode('utf-8'))
    time.sleep(1)

producer.close()