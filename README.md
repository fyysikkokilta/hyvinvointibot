# Hyvinvointibot

Hyvinvointibot is a Telegram bot based on [telepot](https://telepot.readthedocs.io/en/latest/) that was used in the 2018 well-being competition (hyvinvointikilpailu) of the Guild of Physics.
It works by asking questions from users and storing the answers and associated good or bad scores into a MongoDB database.

## Usage
1. Install dependencies:
    ```
    sudo apt install mongodb
    sudo pip3 install pymongo telepot
    ```
    If you want to run the analysis script, you should also `sudo pip3 install numpy matplotlib`.
1. `git clone https://github.com/fyysikkokilta/hyvinvointibot.git && cd hyvinvointibot`.
1. Put your bot token in `token.txt` in the root directory of the repo
1. Check the competititon start and end dates in ???
1. Run the bot: `python3 hyvinvointibot.py`
1. If you want to analyze the data in the database, run `python3 dbmanager.py --export` and update `data_filename` in `analysis.py`, and then run `python3 analysis.py`. Check the source code for details.
