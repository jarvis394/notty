<p align="center"><img width=512 src="https://raw.githubusercontent.com/jarvis394/notty/master/notty.png" alt="terminal view" /></p>
<h1 align="center">notty</h1>
<h6 align="center">📝⚡ Fast terminal-based notes application</h6>

## Setup

Installation via `pip`:

```bash
$ pip install notty
```

Updating:

```bash
$ pip install notty --upgrade
```

Executing:
```bash
$ notty
Usage: notty [OPTIONS] COMMAND [ARGS]...
```

**If you're using Anaconda:**
1. Create new virtual environment
    ```bash
    (base) $ conda create -n YOURNAME python=3
    Collecting package metadata (current_repodata.json): done
    Solving environment: done
    ... # hit [y] for the packages' installation
    ```
2. Activate newly created environment
    ```bash
    (base) $ conda activate YOURNAME
    (YOURNAME) $
    ```
3. Install via `pip`:
    ```bash
    (YOURNAME) $ pip install notty --upgrade
    ```
4. To return to the `(base)` environment, run `conda deactivate`:
    ```bash
    (YOURNAME) $ conda deactivate
    (base) $ 
    ```

*Currently built for **Python 3.x***

## Usage

For more information, run `notty --help`

|Command|Aliases|Description|
|-|-|-|
|create|*c, create*|Creates a new note|
|list|*l, list*|Lists all notes.<br />Actually, it can create, delete, rename the notes, so it might be the most important thing here|
|edit `<id>`|*e, edit*|Edits the note with a given ID (opens up a default editor)|

## Contribution

...is welcomed. PR's are widely opened.

## Contact

Me: [VK](https://vk.com/tarnatovski)
