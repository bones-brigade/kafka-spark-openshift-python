"""spark-kafka-openshift skeleton

This is a skeleton application for processing stream data from Apache
Kafka with Apache Spark. It will read messages on an input topic and
simply echo those message to the output topic.

For an entry point to adding your own processing component, examine
the `EchoStreamProcessor` class and its `configure_processing`
function.
"""


import argparse
import os
import re

import kafka
import pyspark
from pyspark import streaming
from pyspark.streaming import kafka as kstreaming


class EchoStreamProcessor():
    """A class to echo Kafka stream data

    This class wraps the Spark and Kafka specific logic for creating a
    DStream and applying processing functions to the RDDs contained
    therein.

    It is meant as an example of how to configure a processor to read
    from Kafka and write data back to Kafka. See the
    `configure_processing` function for a place to add your custom
    modifications.
    """
    def __init__(self, input_topic, output_topic, servers, duration):
        """Create a new StreamProcessor

        Keyword arguments:
        input_topic -- Kafka topic to read messages from
        output_topic -- Kafka topic to write message to
        servers -- A list of Kafka brokers
        duration -- The window duration to sample the Kafka stream in
                    seconds
        """
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.servers = servers
        self.spark_context = pyspark.SparkContext(
            appName='spark-kafka-skeleton')
        self.streaming_context = streaming.StreamingContext(
            self.spark_context, duration)
        self.kafka_stream = kstreaming.KafkaUtils.createDirectStream(
            self.streaming_context,
            [self.input_topic],
            {'bootstrap.servers': self.servers})

    def configure_processing(self):
        """Configure the processing pipeline

        This function contains all the stream processing
        configuration that will affect how each RDD is processed.
        It will be called before the stream listener is started.
        """
        def send_response(rdd):
            """A function to publish an RDD to a Kafka topic"""
            producer = kafka.KafkaProducer(bootstrap_servers=self.servers)
            for r in rdd.collect():
                producer.send(self.output_topic, r)
            producer.flush()

        messages = self.kafka_stream.map(lambda m: m[1])
        messages.foreachRDD(send_response)

    def start_and_await_termination(self):
        """Start the stream processor

        This function will start the Spark-based stream processor,
        it will run until `stop` is called or an exception is
        thrown.
        """
        self.configure_processing()
        self.streaming_context.start()
        self.streaming_context.awaitTermination()

    def stop(self):
        """Stop the stream processor"""
        self.streaming_context.stop()


def main():
    """The main function

    This will process the command line arguments and launch the main
    Spark/Kafka monitor class.
    """
    parser = argparse.ArgumentParser(
        description='process data with Spark, using Kafka as the transport')
    parser.add_argument('--in', dest='input_topic',
        help='the kafka topic to read data from')
    parser.add_argument('--out', dest='output_topic',
        help='the kafka topic to publish data to')
    parser.add_argument('--servers', help='the kafka brokers')
    args = parser.parse_args()

    processor = EchoStreamProcessor(
        input_topic = args.input_topic,
        output_topic = args.output_topic,
        servers = args.servers,
        duration = 3)

    processor.start_and_await_termination()


if __name__ == '__main__':
    main()

