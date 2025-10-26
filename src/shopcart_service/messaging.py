import pika
import json
import os
import time
from sqlalchemy.orm import Session
from . import crud
from .core.db import SessionLocal


class RabbitMQConsumer:
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'admin')
        self.password = os.getenv('RABBITMQ_PASS', 'admin123')
        
    def get_connection(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)
    
    def callback(self, ch, method, properties, body):
        """Handle incoming user.created events"""
        try:
            message = json.loads(body)
            print(f"📨 Received message: {message}")
            
            if message.get('event_type') == 'user.created' and message.get('is_active'):
                user_uuid = message['user_uuid']
                
                # Create cart for the user
                db: Session = SessionLocal()
                try:
                    cart = crud.create_cart(db, user_uuid)
                    print(f"✅ Created cart for user {user_uuid}: Cart ID {cart.id}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"❌ Failed to create cart: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                finally:
                    db.close()
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages from RabbitMQ"""
        while True:
            try:
                connection = self.get_connection()
                channel = connection.channel()
                
                # Declare exchange
                channel.exchange_declare(
                    exchange='user_events',
                    exchange_type='topic',
                    durable=True
                )
                
                # Declare queue
                channel.queue_declare(
                    queue='shopcart_user_events',
                    durable=True
                )
                
                # Bind queue to exchange
                channel.queue_bind(
                    exchange='user_events',
                    queue='shopcart_user_events',
                    routing_key='user.created'
                )
                
                # Set prefetch count
                channel.basic_qos(prefetch_count=1)
                
                # Start consuming
                channel.basic_consume(
                    queue='shopcart_user_events',
                    on_message_callback=self.callback
                )
                
                print('🎧 Waiting for messages. To exit press CTRL+C')
                channel.start_consuming()
                
            except KeyboardInterrupt:
                print("Stopping consumer...")
                break
            except Exception as e:
                print(f"❌ Connection error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)


def start_consumer():
    """Entry point for consumer"""
    consumer = RabbitMQConsumer()
    consumer.start_consuming()