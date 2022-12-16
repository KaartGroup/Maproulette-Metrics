# Maproulette Metrics Scripts

## Installation

1. Unzip the archive (if you're reading this, you may have already done this)
2. Open a Terminal window
3. Run `cd /path/to/unzipped/folder`
4. Run `pip3 install .`

## Setting API Key

1. Open our Maproulette instance in a browser
2. Sign in if necessary
3. Click your username in the top-right corner of the page
4. Select "User Settings"
5. Scroll to the bottom of the page, where you should find the section labelled "API KEY"
6. Copy the key
7. In the Terminal, run `set_maproulette_key`
8. When prompted, paste your key with Cmd-V, then hit return. Note that you will not see your key after you paste it; this is normal and a security feature

## Getting Metrics

### Numeric IDs

MapRoulette uses a numeric user id for each user; this is unique to each server, so a given editor will have a different ID on the public Maproulette server as on a private server. The first time that the script (on a particular computer) sees a user, it checks the server to get that user's numeric ID, and then stores it. Every time thereafter (on that computer), the script will use its local copy of the user's ID instead of going to the server.

### Using the script

Run
`get_maproulette_metrics [--metric-type {editor,qc}] users output start [end]`
_[Square brackets] indicate optional arguments, {curly braces} indicate mutually-exclusive choices._

For example, `get_maproulette_metrics ~/Documents/sinopah.txt ~/Documents/april_03_metrics.xlsx 2022-04-03` will get metrics for all the users in the file "sinopah.txt",
from April 3 until today's date, and save to a spreadsheet called "april_03_metrics.xlsx".

Adding a date to the end, like `get_maproulette_metrics ~/Documents/sinopah.txt ~/Documents/april_03_metrics.xlsx 2022-04-03 2022-04-08`, will do the same for April 3 until April 8, inclusive.

Adding `--metric-type qc` anywhere, for example `get_maproulette_metrics --metric-type qc ~/Documents/sinopah.txt ~/Documents/april_03_metrics.xlsx 2022-04-03 2022-04-08` will query QC metrics instead.
