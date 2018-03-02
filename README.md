# spark-kafka-openshift-skeleton

A Python source-to-image application skeleton for using Apache Spark and
Kafka on OpenShift.

This application will simply read messages from a Kafka topic, and
the write those messages back out to a second topic. It will achieve this
using Spark's streaming utilities for Kafka.

## usage on openshift

As this project utilizes Spark, it will be easiest to consume on OpenShift by
using the [RADanalytics](https://radanalytics.io) tooling. The source-to-image
nature of this application will require that a Spark cluster is available. The
shortest path to making that connection is to use the automatically spawned
Spark clusters that are created by the
[Oshinko project source-to-image](https://github.com/radanalyticsio/oshinko-s2i)
utilities. Please see that documentation for more information about this
process.

This application also requires the deployment of a Kafka broker and something
to emit messages to that broker. These topics are out of scope for this
tutorial, but please see
[this tutorial on radanalytics.io](https://radanalytics.io/applications/grafzahl)
for some inspiration on prototyping this process.

1. see the [radanalytics.io Get Started page](https://radanalytics.io/get-started)
   for instructions on installing that tooling

1. launch the skeleton with the following command:
   ```bash
   oc new-app --template=oshinko-python-build-dc \
              -p APPLICATION_NAME=skeleton \
              -p GIT_URI=https://github.com/bones-brigade/kafka-spark-openshift-python \
              -p APP_ARGS='--servers=apache-kafka:9092 --in=topic1 --out=topic2'  \
              -p SPARK_OPTIONS='--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0'
   ```

In this example, our application will subscribe to messages on the Kafka topic
`topic1`, and it will publish messages on the topic `topic2` using the broker
at `apache-kafka:9092`.

## extending this project

The source code of this application is documented to help new developers with
a rapid start to building their own processing applications. Please see the
`app.py` file for more documentation on modifying the behavior of this
project.
