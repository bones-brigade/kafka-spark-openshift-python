"""kafka-spark-openshift-python

This is a skeleton application for processing stream data from Apache
Kafka with Apache Spark. It will read messages on an input topic and
simply echo those message to the output topic.

This application uses Spark's _Structured Streaming_ interface, for
more information please see
https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
"""

import argparse
import logging
import os
import shutil
import urllib.request as urllib

import pyspark.sql as sql
import pyspark.sql.types as types
import pyspark.sql.functions as functions


def main(args):
    """Configure and start the Kafka stream processor"""
    # acquire a SparkSession object
    spark = (
        sql
        .SparkSession
        .builder
        .appName('kafka-spark-openshift-python')
        .getOrCreate()
    )

    # if a user function is specified, download it and import it
    if args.userfunction is not None:
        try:
            logging.info('downloading user function')
            logging.info(args.userfunction)
            dl = urllib.urlretrieve(args.userfunction)
            shutil.copyfile(dl[0], '/opt/app-root/src/userfunction.py')
            import userfunction
            user_function = functions.udf(
                userfunction.main,  types.StringType())
            logging.info('user function loaded')
        except Exception as e:
            logging.error('failed to import user function file')
            logging.error(e)
            user_function = None

    # configure the operations to read the input topic
    records = (
        spark
        .readStream
        .format('kafka')
        .option('kafka.bootstrap.servers', args.brokers)
        .option('subscribe', args.intopic)
        .load()
        .select(
            functions.column('value').cast(types.StringType()).alias('value'))
        # add your data operations here, the raw message is passed along as
        # the alias `value`.
        #
        # for example, to process the message as json and create the
        # corresponding objects you could do the following:
        #
        # .select(
        #     functions.from_json(
        #         functions.column('value'), msg_struct).alias('json'))
        #
        # the following operations would then access the object and its
        # properties using the name `json`.
    )

    # if it exists, add the user function to the stream pipeline
    if user_function is not None:
        records = (
            records
            .select(user_function(functions.column('value')).alias('value'))
        )

    # configure the output stream
    writer = (
        records
        .writeStream
        .format('kafka')
        .option('kafka.bootstrap.servers', args.brokers)
        .option('topic', args.outtopic)
        .option('checkpointLocation', '/tmp')
        .start()
    )

    # begin processing the input and output topics
    writer.awaitTermination()


def get_arg(env, default):
    return os.getenv(env) if os.getenv(env, '') is not '' else default


def parse_args(parser):
    args = parser.parse_args()
    args.brokers = get_arg('KAFKA_BROKERS', args.brokers)
    args.intopic = get_arg('KAFKA_IN_TOPIC', args.intopic)
    args.outtopic = get_arg('KAFKA_OUT_TOPIC', args.outtopic)
    args.userfunction = get_arg('USER_FUNCTION_URI', args.userfunction)
    return args


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('starting kafka-spark-openshift-python')
    parser = argparse.ArgumentParser(
            description='copy messages from one stream to another')
    parser.add_argument(
            '--brokers',
            help='The bootstrap servers, env variable KAFKA_BROKERS',
            default='localhost:9092')
    parser.add_argument(
            '--in-topic',
            dest='intopic',
            help='Topic to publish to, env variable KAFKA_TOPIC',
            default='topic1')
    parser.add_argument(
            '--out-topic',
            dest='outtopic',
            help='Topic to publish to, env variable KAFKA_TOPIC',
            default='topic2')
    parser.add_argument(
            '--user-function',
            dest='userfunction',
            help='URI to a user function .py file, env variable '
            'USER_FUNCTION_URI')
    args = parse_args(parser)
    main(args)
    logging.info('exiting')
