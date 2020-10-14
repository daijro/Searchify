# Searchify
Brainly/quizlet searcher


Heres a small program I wrote to help with Edgenuity... Its currently only in a beta so there still might be some bugs. It might be a little slow right now but I've tried everything I can to optimize it lol

Heres some screenshots of the [dark theme](https://i.imgur.com/HOywNMb.png), [black theme](https://i.imgur.com/56CP26a.png), and [light theme](https://i.imgur.com/0WvHxCt.png)


## [Download v1.2.0 installer](https://www.dropbox.com/s/r2h2qauqrtthc2x/Searchify%20v1.2.0%20Installer%20%28x64%29.exe?dl=1)

## [Download v1.2.0 zip](https://www.dropbox.com/s/voo14pac7dnx177/Searchify%20v1.2.0p%20%28x64%29.zip?dl=1)

#### Previous Versions:

#### [Download v1.1.3 installer](https://www.dropbox.com/s/9ivknsm2v5vha88/Searchify%20v1.1.3%20Installer%20%28x64%29.exe?dl=1)

#### [Download v1.1.3 zip](https://www.dropbox.com/s/469hwiv62xqke1z/Searchify%20v1.1.3p%20%28x64%29.zip?dl=1)


---
### Requirements for source code (requires python 3.8+):

If you are downloading the source code, please run this command to install the libraries needed:
```
python -m pip install requests requests-html beautifulsoup4 python-Levenshtein PyQt5
```



---


### Whats new in v1.1.3:
- Fixed the "too many requests error" for google
- Added bing and yahoo searching
- Fixed errors in brainly parsing



### What it does:

- Search the first page of google for brainly and quizlet results

- Sort results by how similar the identified question is to the input question

- Parse the websites all at the same time (takes a lot of CPU)

- In quizlet sets, it finds which flashcard is the most similar to the input question

- In brainly, it gets all of the answers and how many Thanks each answer gets

- Toggle brainly and/or quizlet searching on and off

- Automatically switch to DuckDuckGo if Google isn't working

### Future plans:

- Add a built-in paraphraser

- Add button to input from clipboard

- Add hotkeys

- Add other sites (such as quizizz)

- Maybe add a mathway section ?

- Idk i need suggestions


### Known issues:

- Too many requests error

- Very slow on low end laptops

- The UI margins can be glitched

- Brainly answers with formatting aren't parsed correctly

- Complicated questions act weird
