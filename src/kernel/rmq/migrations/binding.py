from abc import ABC, abstractmethod

from aio_pika.abc import AbstractExchange, AbstractQueue

from src.kernel.rmq.connector import BaseRMQConnector
from src.kernel.rmq.models import RmqBinding


class AbstractRmqBinder(ABC):
    @abstractmethod
    async def declare(self, binding: RmqBinding) -> None:
        pass


class BaseRmqBinder(AbstractRmqBinder):
    def __init__(self, connector: BaseRMQConnector):
        self._connector = connector

    async def __get_queue(self, binding: RmqBinding) -> AbstractQueue:
        async with self._connector.channel_pool.acquire() as channel:
            return await channel.get_queue(binding.queue)

    async def __get_exchange(self, binding: RmqBinding) -> AbstractExchange:
        async with self._connector.channel_pool.acquire() as channel:
            return await channel.get_exchange(binding.exchange)

    async def declare(self, binding: RmqBinding) -> None:
        queue = await self.__get_queue(binding)
        exchange = await self.__get_exchange(binding)
        await queue.bind(exchange, **binding.kwargs)
