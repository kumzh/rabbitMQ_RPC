import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'
))

channel = connection.channel()
channel.queue_declare(queue='rpc_queue')
def fib(n):  #生成斐波那契数
    if n == 0:
        return 0
    elif n  == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

def on_request(ch,method,props,body):
    n = int(body)

    print("[.] fib(%s)"%n)
    response = fib(n)
    #publishf返回消息
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=\
                                                     props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag= method.delivery_tag)

channel.basic_consume(on_message_callback=on_request,queue='rpc_queue')

print("[X] a waiting RPC request")

channel.start_consuming()
