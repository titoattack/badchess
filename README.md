This is a bad program where you can play chess.
It's both a chess engine (play moves) and a chess GUI (user interface).
Why it's so bad? Because I just started coding. I'm learning and I will improve it over time.

## HOW TO USE IT ##

Run the 'badchess.py' file present in the src/ directory using python3 interpreter:

### `$: python3 badchess.py`

By default, white player is the user and black is the engine.
If you want to choose what plays what (user or engine, either black or white), change it at the start of the file 'badchess.py'.

## WHY IT IS SO BAD ##

There are many design problems I'm aware (and much more that I don't). One of the biggest problems is an intensive 
and inneficient reliance on deepcopying stateboard arrays, due to a lack of a backmove function.
Because of that, the minimax algorithm is set by default to calculate just up to 2 ply (singular moves), which is absolutely terrible even for a python implementation.


I intend on recreating the chess infrastructure and search algorithm in Rust, which will happen as soon as I learn enough Rust.
