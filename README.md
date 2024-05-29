# Queens

This is the clone of the Queens game on [Linkedin](https://www.linkedin.com/games/queens/) that lets you play on demand, since my queen (girlfriend) and I hate waiting until 2am CST for a new board to come out.

Install the game with the following command:
```
pip install -r requirements.txt
```

Run the game with the following command:
```
python3 queens.py
```

## Controls
- Left click to toggle between X'ing out a square, placing a queen, and emptying a square
- Right click to place a question mark (for when you're unsure of a square)
  - Question marks can only be placed on empty squares, and you must remove the question mark to X out a square or place a queen
- Click "New Game" for a new board
- Click "Check Board" to check whether you've incorrectly X'ed out a square or incorrectly placed a queen
  - **WARNING**: Making sure there is only one solution is TODO, so this may not be totally accurate
- Click on "Give Up :(" if you suck (jk)
