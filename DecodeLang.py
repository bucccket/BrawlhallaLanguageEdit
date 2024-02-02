import zlib
import io

class UTF8String:
    @classmethod
    def FromBytesIO(cls, data):
        length = cls.__ReadUint16BE(data)
        string = data.read(length).decode('utf-8')
        return cls(length, string)
    
    @classmethod
    def FromString(cls, string):
        return cls(len(string), string)
    
    def __init__(self, length, string):
        self.length = length
        self.string = string

    def __ReadUint16BE(data):
        byte = data.read(2)
        return int.from_bytes(byte, byteorder="big")  # whar?

class Entry:
    @classmethod
    def FromBytesIO(cls, data):
        return cls(UTF8String.FromBytesIO(data), UTF8String.FromBytesIO(data))
    
    @classmethod
    def FromKeyValuePair(cls, key, value):
        return cls(UTF8String.FromString(key), UTF8String.FromString(value))
    
    def __init__(self, key, value):
        self.key = key
        self.value = value

class LangFile:

    def __init__(self, filename):
        fd = open(filename, "rb")

        self.entries = []

        self.inflated_size = fd.read(4)
        self.zlibdata = fd.read()

        self.__ParseFile()

    def __ParseFile(self):
        self.data = io.BytesIO(zlib.decompress(self.zlibdata))
        self.entry_count = self.__ReadUint32BE(self.data)

        while len(self.entries) < self.entry_count:
            self.entries.append(Entry.FromBytesIO(self.data))
        pass

    def __ReadUint32BE(self, data):
        byte = data.read(4)
        return int.from_bytes(byte, byteorder="big")  # whar?

    def __setitem__(self, key, value):
        for entry in self.entries:
            if entry.key.string == key:
                entry.value.string = value
                return
        self.entries.append(Entry.FromKeyValuePair(key, value))
        self.entry_count += 1
        
    def __getitem__(self, key):
        for entry in self.entries:
            if entry.key.string == key:
                return entry.value.string
        return None

if __name__ == "__main__":
    langfile = LangFile("language.1.bin")
    langfile["test"] = "test"
    print(langfile['MirageColorSchemeType_Black_DisplayName'])
    pass