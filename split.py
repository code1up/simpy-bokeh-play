"""DOCSTRING"""
import simpy

from random import randint

QUEUE_CAPACITY_BYTES = 4096
MESSAGE_BLOCK_SIZE = 1024
MESSAGE_BLOCK_TIMEOUT = 200


class Message:
    """DOCSTRING"""
    __slots__ = [
        'size',
        'correlation_id'
    ]

    def __init__(self, correlation_id, size):
        self.correlation_id = correlation_id
        self.size = size


class MessageQueue:

    """DOCSTRING"""
    __slots__ = [
        'env',
        'capacity'
    ]

    def __init__(self, env, capacityBytes):
        self.env = env
        self.capacity = simpy.Container(
            env=env,
            capacity=capacityBytes,
            init=capacityBytes)

    def queue_message(self, message):
        """DOCSTRING"""
        if message.size > MESSAGE_BLOCK_SIZE:
            yield self.env.process(generator=self.splitting(message))

        else:
            try:
                yield self.waiting_for_capacity(message)
                yield self.traversing(message)
                yield self.traversed(message)

            except simpy.events.Interrupt:
                self.abandoned(message)

    def waiting_for_capacity(self, message):
        self.log(message=message, state='waiting for capacity')
        return self.capacity.get(amount=message.size)

    def traversing(self, message):
        self.log(message=message, state='traversing')

        latency = randint(50, 80)
        return self.env.timeout(delay=latency)

    def traversed(self, message):
        self.log(message=message, state='traversed')
        return self.capacity.put(amount=message.size)

    def splitting(self, message):
        self.log(message=message, state='splitting')

        message_blocks = self.split_message(message)
        message_events = []

        for each in message_blocks:
            message_events.append(
                self.env.process(generator=self.queue_message(each)))

        timeout = self.env.timeout(delay=MESSAGE_BLOCK_TIMEOUT)

        completed_events = yield simpy.events.AllOf(
            env=self.env, events=message_events) | timeout

        if timeout in completed_events:
            self.abandon_incomplete_messages(
                message=message,
                message_events=message_events,
                completed_events=completed_events)

            return

        self.log(message=message, state='traversed large message')

    def abandon_incomplete_messages(self, message, message_events, completed_events):
        for each in message_events:
            if each not in completed_events:
                each.interrupt(cause='timed out')

        self.log(message=message, state='timed out large message')

    def abandoned(self, message):
        self.log(message=message, state='abandoned')
        return self.capacity.put(amount=message.size)

    def split_message(self, message):
        message_blocks = []

        completeBlockCount = message.size // MESSAGE_BLOCK_SIZE
        partialBlockSize = message.size % MESSAGE_BLOCK_SIZE

        messageCount = completeBlockCount + (0 if partialBlockSize == 0 else 1)

        for n in range(messageCount):
            correlation_id = f'{message.correlation_id}.{n + 1}'

            size = MESSAGE_BLOCK_SIZE \
                if n < completeBlockCount \
                else partialBlockSize

            message_block = Message(correlation_id=correlation_id, size=size)
            message_blocks.append(message_block)

        return message_blocks

    def log(self, message, state):
        s = f'message {message.correlation_id} {state} at {self.env.now} [{message.size}]'
        print(s)


def main():
    """DOCSTRING"""

    message_a = Message(correlation_id='A', size=MESSAGE_BLOCK_SIZE - 1)
    message_b = Message(correlation_id='B', size=(MESSAGE_BLOCK_SIZE * 4) + 1)
    message_c = Message(correlation_id='C', size=MESSAGE_BLOCK_SIZE)
    message_d = Message(correlation_id='D', size=MESSAGE_BLOCK_SIZE + 1)
    message_e = Message(correlation_id='E', size=MESSAGE_BLOCK_SIZE - 1)

    env = simpy.Environment()

    queue = MessageQueue(env=env, capacityBytes=QUEUE_CAPACITY_BYTES)

    env.process(queue.queue_message(message=message_a))
    env.process(queue.queue_message(message=message_b))
    env.process(queue.queue_message(message=message_c))
    env.process(queue.queue_message(message=message_d))
    env.process(queue.queue_message(message=message_e))

    env.run()


if __name__ == '__main__':
    main()
