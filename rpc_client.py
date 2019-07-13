import pika
import uuid  #用于生成一个随机字符串
import time

class FibonacciRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'
        ))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare( queue='',exclusive=True)

        self.callback_queue =result.method.queue

        self.channel.basic_consume(on_message_callback=self.on_response,  #收到消息就执行该函数
                                   auto_ack=False,
                                   queue=self.callback_queue)

    def on_response(self,ch,method,props,body):
        '''回调函数，每次收到回复后执行。收到回复后会检查ID是否一致，一致则接收。
        为了防止在多client场景无法正确收到消息的情况。
        '''
        if self.corr_id == props.correlation_id:
            self.response = body


    #call函数用于向外发消息。
    def call(self,n):
        self.response = None #初始化接收的消息为NONE
        self.corr_id = str(uuid.uuid4())#为每一次交互生成一个ID
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(n))
        #如果为空则一直接收
        while self.response is None:
            self.connection.process_data_events() #非阻塞班的start-consuming，没收到消息也会返回
            print('no message....')
            time.sleep(0.5)
        return int(self.response)

fibonacci_rpc = FibonacciRpcClient()

print('[X] Requesting fib(30)')
response = fibonacci_rpc.call(6)

print('[.] Got %r'%response)
