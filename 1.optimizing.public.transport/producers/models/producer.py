"""Producer base-class providing common utilites and functionality"""
import logging
import time
import socket

from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)


class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        # Configure the broker properties to use the Host URL for Kafka and Schema Registry!
        #
        self.broker_properties = {
            'bootstrap.servers': 'PLAINTEXT://localhost:9092',
            'schema.registry.url': 'http://localhost:8081',
            'client.id': socket.gethostname()
        }

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # Configure the AvroProducer
        self.producer = AvroProducer(
            config=self.broker_properties,
            default_key_schema=self.key_schema,
            default_value_schema=self.value_schema
        )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        #
        # Create topic for this producer if it does not already exist on the Kafka Broker.

        client = AdminClient(conf={'bootstrap.servers': self.broker_properties['bootstrap.servers']})

        if not self._does_topic_exist(self.topic_name, client=client):
            logger.info(f"WARNING: Topic {self.topic_name} already exists - skipping")
            return
        topic = NewTopic(
            topic=self.topic_name,
            num_partitions=self.num_partitions,
            replication_factor=self.num_replicas
        )

        futures = client.create_topics([topic])

        for topic, future in futures.items():
            try:
                future.result()
                logger.debug(f"SUCCESS: Topic {self.topic_name} created!")
            except Exception as e:
                logger.debug(f"WARNING: Topic {self.topic_name} already exists")

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""

        # Close Producer
        if not self.producer:
            return
        self.producer.flush()
        logger.info("SUCCESS: Producer closed.")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))

    @staticmethod
    def _does_topic_exist(topic_name: str, client: AdminClient):
        """ Check if topic_name exists in the existing lists of kafka topics """
        meta_data = client.list_topics()
        return topic_name in meta_data.topics
