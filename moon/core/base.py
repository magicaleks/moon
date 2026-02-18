# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Generic, Iterable, Iterator, Optional, TypeVar, Union

from moon.schemas import ArgumentsError

T = TypeVar("T")
R = TypeVar("R")


class StatefulStreamer(ABC, Generic[T, R]):
    def __init__(self, stream: Union[Iterable[T]]) -> None:
        if isinstance(stream, Iterator):
            self.__stream = stream
        elif isinstance(stream, Iterable):
            self.__stream = iter(stream)
        else:
            raise ArgumentsError(
                f"Stream must be an iterator or an iterable but got {type(stream)}"
            )
        self.__current: Optional[T] = None
        self.__next: Optional[T] = None

    def next(self) -> T:
        if self.__next is not None:
            self.__current = self.__next
            self.__next = None
        else:
            self.__current = next(self.__stream)
        return self.__current

    def read(self) -> T:
        if self.__current is None:
            self.__current = self.__next or next(self.__stream)
        return self.__current

    def peek(self) -> Optional[T]:
        if self.__next is None:
            try:
                self.__next = next(self.__stream)
            except StopIteration:
                self.__next = None
        return self.__next

    @abstractmethod
    def __iter__(self) -> Iterator[R]:
        pass
