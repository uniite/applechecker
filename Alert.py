import boto3
import smtplib
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from socket import gaierror


class BaseAlert(object):
    def _print_ahead(self, method):
        def wrapper(msgbody):
            print(msgbody)
            method(msgbody)
        return wrapper


class SnsAlert(BaseAlert):
    def __init__(self, topic_arn):
        sns = boto3.resource('sns')
        self.topic = sns.Topic(arn=topic_arn)

    def send(self, message, attributes={}):
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.

        :param topic: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return: The ID of the message.
        """
        topic = self.topic
        try:
            att_dict = {}
            for key, value in attributes.items():
                if isinstance(value, str):
                    att_dict[key] = {'DataType': 'String', 'StringValue': value}
                elif isinstance(value, bytes):
                    att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
            response = topic.publish(Message=message, MessageAttributes=att_dict)
            message_id = response['MessageId']
            print("Published message with attributes %s to topic %s." % (attributes, topic.arn))
        except ClientError:
            print("Couldn't publish message to topic %s." % topic.arn)
            raise
        else:
            return message_id


class SmtpAlert(BaseAlert):
    def __init__(self, dest=None, login=None, password=None):
        self.dest = dest
        self.login = login
        self.password = password
        self.send = self._print_ahead(self.send_smtp)

    def send_smtp(self, msgbody):
        return
        message = MIMEText(msgbody, _charset="UTF-8")
        message['From'] = self.login
        message['To'] = self.dest
        message['Subject'] = "Apple Stock Alert"

        try:
            mailer = smtplib.SMTP('smtp.gmail.com:587')
        except gaierror:
            print("Couldn't reach Gmail server")
            return
        mailer.ehlo()
        mailer.starttls()
        mailer.ehlo()
        mailer.login(self.login, self.password)
        mailer.sendmail(self.login, self.dest, message.as_string())
        mailer.close()
