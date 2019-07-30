# kafka-spark-python

A Python source-to-image application skeleton for using Apache Spark and
Kafka on OpenShift.

This application will simply read messages from a Kafka topic, and
the write those messages back out to a second topic. It will achieve this
using Spark's streaming utilities for Kafka.

## Prerequisites

* OpenShift - this application is designed for use on OpenShift, you can find
  great documentation and starter guides
  [on their website](https://docs.openshift.org/latest/getting_started/index.html).

* Apache Kafka - because this application requires a Kafka broker to read from
  and write to, you will need to a broker deployed and a source of
  information. The Strimzi project provides some great
  [documentation and manifests](http://strimzi.io/) for running Kafka on
  OpenShift.

### Helpful tools

To help accelerate work with Kafka, here are a few applications to help:

* [Emitter](https://gitlab.com/bones-brigade/kafka-python-emitter) -
  this is a skeleton to publish text information on a Kafka topic.

* [Listener](https://gitlab.com/bones-brigade/kafka-python-listener) -
  this is a skeleton to log all messages from a Kafka topic.

## Quickstart

As this project utilizes Spark, it will be easiest to consume on OpenShift by
using the [RADanalytics](https://radanalytics.io) tooling. The source-to-image
nature of this application will require that a Spark cluster is available. The
shortest path to making that connection is to use the automatically spawned
Spark clusters that are created by the
[Oshinko project source-to-image](https://github.com/radanalyticsio/oshinko-s2i)
utilities. Please see that documentation for more information about this
process.

1. see the [radanalytics.io Get Started page](https://radanalytics.io/get-started)
   for instructions on installing that tooling

1. launch the skeleton with the following command:
   ```bash
   oc new-app --template=oshinko-python36-spark-build-dc \
              -p APPLICATION_NAME=skeleton \
              -p GIT_URI=https://gitlab.com/bones-brigade/kafka-spark-python \
              -e KAFKA_BROKERS=localhost:9092 \
              -e KAFKA_IN_TOPIC=topic1 \
              -e KAFKA_OUT_TOPIC=topic2 \
              -p SPARK_OPTIONS='--packages=org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0'
   ```

In this example, our application will subscribe to messages on the Kafka topic
`topic1`, and it will publish messages on the topic `topic2` using the broker
at `apache-kafka:9092`.

## Adding functionality through a user defined function

You can extend the functionality of this application by creating a user
defined function which will get called for every message that is written to
the input topic.

With a user defined function you can modify, or even omit, the data before it
is written onto the second topic. For a simple example see the
[wrapper.py](examples/wrapper.py) file in the examples directory.

To utilize an external user defined function it must exist in a file that
can be downloaded by your continerized application. The environment
variable `USER_FUNCTION_URI` must contain the URI to the file. Here is an
example using the previous launch command and the `wrapper.py` file from this
repository:

```bash
   oc new-app --template=oshinko-python36-spark-build-dc \
              -p APPLICATION_NAME=skeleton \
              -p GIT_URI=https://gitlab.com/bones-brigade/kafka-spark-python \
              -e KAFKA_BROKERS=localhost:9092 \
              -e KAFKA_IN_TOPIC=topic1 \
              -e KAFKA_OUT_TOPIC=topic2 \
              -p SPARK_OPTIONS='--packages=org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0'
              -e USER_FUNCTION_URI='https://gitlab.com/bones-brigade/kafka-spark-python/raw/master/examples/wrapper.py'
```

### User defined function API

The API for creating a user defined function is fairly simple, there are three
rules to crafting a function:

1. There must be a top-level function named `user_defined_function`. This
   is the main entry point into your feature, the main application will look
   for this function.
1. Your function must accept a single argument. The function will be passed
   a string type variable that contains the message as it was broadcast onto
   the Kafka topic.
1. Your function must return either a string or `None`. If your function
   returns a string, that string will be broadcast to the output topic. If
   it returns `None`, nothing will be broadcast.
