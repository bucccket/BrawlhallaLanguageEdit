# BrawlhallaLanguageEdit

## How To Use

This Wrapper Implements deserialization of the language.#.bin files

To use it just construct a new **LangFile** object. You can treat the object like a dict, when acessing and modifying items.

### Example

```py
from DecodeLang import LangFile

if __name__ == "__main__":
    langfile = LangFile("language.1.bin")
    langfile["test"] = "test"
    print(langfile['MirageColorSchemeType_Black_DisplayName'])
```

### Note

this project is missing serialization as of now so you cannot write to the file (yet)
