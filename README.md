# BrawlhallaLanguageEdit

## How To Use

This wrapper implements deserialization and serialization of the language.#.bin files

To use it just construct a new **LangFile** object. You can treat the object like a dict, when acessing and modifying items.

### Example

```py
if __name__ == "__main__":
    langfile = LangFile("language.1.bin.og") # open file
    langfile["test"] = "test" # create new entry
    langfile["UI_PHASE_DESCRIPTION_SUCCESS_NONE"] = "Launched your mom into space" # change existing entry
    print(langfile['MirageColorSchemeType_Black_DisplayName']) # read entry
    langfile.Save("language.1.bin") # save file
```
