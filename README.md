# wikivoyage

Consume [Wikivoyage](https://en.wikivoyage.org) into pure (elegant) Markdown. Probably.

```
$ pip install wikivoyage
```

## Usage

Just do what you want.

```python
import wikivoyage

# Learn about the States
res = wikivoyage.get("https://en.wikivoyage.org/wiki/United_States_of_America")
print(res)
```

```python
WikivoyageSections(
    url='https://en.wikivoyag…',
    sections=[
        Section(
            title='United States of America', 
            content='The **United States of America** spans a continent…'
        ), 
        Section(
            title='Regions', 
            content="Wikivoyage organizes the 50 states and the nation'…"
        ), 
        Section(
            title='Cities', 
            content='The following is a list of nine of the most notabl…'
        ),
        ...
    ]
)
```

Super simple.

## Why?

I'm initially a "i aint reading allat" person, thus I made this project so I can better categorize all the sections from a Wikivoyage page, feed it to an LLM and summarize it for me.

Check out [where-next](https://github.com/AWeirdDev/where-next), a Next.JS project created by me to learn more.

## API Reference

The juicy API reference. Press <kbd>CTRL + F</kbd> to search for what you need or type directly in the search bar if you're on mobile.

### <kbd>def</kbd> get()

```python
get(url: str, **requests_kwargs) -> WikivoyageSections
```

Fetches a Wikivoyage page and parses it into Markdown.

**Args**:
- url (str): The URL.
- \*\*requests_kwargs: Keyword-only arguments to pass into `requests.get`.

**Returns**:<br />
WikivoyageSections: Wikivoyage sections.

### <kbd>dataclass</kbd> WikivoyageSections

Represents all the Wikivoyage sections. *(manually-created)*

```python
class WikivoyageSections:
    url: str  # The request URL
    sections: List[Section]  # Sections
```

### <kbd>dataclass</kbd> Section

Repersents a Wikivoyage section. *(manually-created)*

```python
class Section:
    title: str  # The title. Alias: `section`
    content: str  # The content. Alias: `markdown`
```
