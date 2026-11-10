# Aim Trainer

My first project. I built this in 2024 as my diploma minor project.

I played a lot of FPS games back then and wanted to know how aim trainers actually work, so I made a simple one in Pygame and hooked it up to MySQL to keep a leaderboard.

![Gameplay](screenshots/3_gameplay.png)

## How it works

You enter your name, pick a difficulty, and targets start popping up. Each target grows and then shrinks. Click it before it disappears. If you miss 3, the game ends and you get your time, hits and accuracy, along with the top 5 scores saved in the database.

Difficulty only changes how fast targets spawn and how big they get:

- Easy: every 600 ms, size 40
- Medium: every 400 ms, size 30
- Hard: every 250 ms, size 20

More screenshots are in the `screenshots/` folder.

## Running it

You need Python and MySQL.

```
mysql -u root -p < schema.sql
pip install -r requirements.txt
```

Set your DB login as environment variables (I took the hardcoded password out before uploading):

```
# Windows PowerShell
$env:DB_USER="your_user"; $env:DB_PASSWORD="your_password"

# Mac / Linux
export DB_USER=your_user DB_PASSWORD=your_password
```

Then run `python main.py`.

## Things I'd do differently now

- The whole game is in one file. I'd split the game logic, the screens and the DB code.
- Play Again calls `main()` again instead of looping, so it technically keeps stacking calls.
- The leaderboard ranks mostly by accuracy, which isn't a great measure on its own. Something like hits per second would be fairer.
- There's no in-game display of lives or score while you're playing.

Built with Python, Pygame and MySQL.