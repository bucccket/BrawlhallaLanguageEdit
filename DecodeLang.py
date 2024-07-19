import re
from typing import Any
import zlib
import io
import codecs


class UTF8String:

    # ctor
    def __init__(self, length: int, string: str):
        self.length = length
        self.string = string

    # static class methods
    @classmethod
    def FromBytesIO(cls, data: io.BytesIO) -> Any:
        length = cls.__ReadUint16BE(data)
        string = data.read(length).decode('utf-8')
        return cls(length, string)

    @classmethod
    def FromString(cls, string: str) -> Any:
        return cls(len(string.encode('utf-8')), string)

    # public
    def WriteBytesIO(self, data: io.BytesIO) -> None:
        data.write(self.length.to_bytes(2, byteorder="big"))
        data.write(self.string.encode('utf-8'))

    # private
    def __ReadUint16BE(data: io.BytesIO) -> int:
        byte = data.read(2)
        return int.from_bytes(byte, byteorder="big")  # whar?


class Entry:

    # ctor
    def __init__(self, key: UTF8String, value: UTF8String):
        self.key: UTF8String = key
        self.value: UTF8String = value

    # public
    def WriteBytesIO(self, data: io.BytesIO) -> None:
        self.key.WriteBytesIO(data)
        self.value.WriteBytesIO(data)

    def SetValue(self, value: str) -> None:
        self.value = UTF8String.FromString(value)

    # static class methods
    @classmethod
    def FromBytesIO(cls, data: io.BytesIO) -> Any:
        return cls(UTF8String.FromBytesIO(data), UTF8String.FromBytesIO(data))

    @classmethod
    def FromKeyValuePair(cls, key: str, value: str) -> Any:
        return cls(UTF8String.FromString(key), UTF8String.FromString(value))


class LangFile:

    # ctor
    def __init__(self, filename: str):
        fd = open(filename, "rb")

        self.entries = []

        self.inflated_size = fd.read(4)
        self.zlibdata = fd.read()

        self.__ParseFile()

    # public
    def Save(self, filename: str) -> None:

        data: io.BytesIO = io.BytesIO()
        data.write(self.__WriteUint32BE(self.entry_count))
        for entry in self.entries:
            entry.WriteBytesIO(data)

        with open(filename, "wb") as fd:
            self.inflated_size = data.getbuffer().nbytes
            fd.write(self.inflated_size.to_bytes(4, byteorder="little"))
            self.zlibdata = zlib.compress(data.getbuffer())
            fd.write(self.zlibdata)

    def Dump(self, filename: str) -> None:
        with codecs.open(filename, "w", "utf-8") as fd:
            for entry in self.entries:
                fd.write(f"{entry.key.string}={entry.value.string}\n")

    # Please Note that this function does not perform well reading a whole dump
    # There are a lot of issues with encoding that makes it not work properly
    # on special characters
    def FromTextFile(self, filename: str) -> None:
        with codecs.open(filename, "r", "utf-8") as fd:
            data = fd.read()
            regex = re.compile(r"((?:.*_).*)=(.*(?:[^=]*\n)*)")
            matches = regex.findall(data)
            for match in matches:
                self[match[0]] = match[1]

    # private
    def __ParseFile(self) -> None:
        self.data: io.BytesIO = io.BytesIO(zlib.decompress(self.zlibdata))
        self.entry_count: int = self.__ReadUint32BE(self.data)

        while len(self.entries) < self.entry_count:
            self.entries.append(Entry.FromBytesIO(self.data))

    def __ReadUint32BE(self, data: io.BytesIO) -> int:
        byte = data.read(4)
        return int.from_bytes(byte, byteorder="big")  # whar?

    def __WriteUint32BE(self, number: int) -> bytes:
        return number.to_bytes(4, byteorder="big")

    # overrides
    def __setitem__(self, key: str, value: str) -> None:
        for entry in self.entries:
            if entry.key.string == key:
                entry.SetValue(value)
                return
        self.entries.append(Entry.FromKeyValuePair(key, value))
        self.entry_count += 1

    def __getitem__(self, key: str) -> (str | None):
        for entry in self.entries:
            if entry.key.string == key:
                return entry.value.string
        return None
