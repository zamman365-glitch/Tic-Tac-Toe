# Tic-Tac-Toe with MySQL Database

A Python-based Tic-Tac-Toe game where players can play against the computer and their game statistics are stored in a MySQL database.

## Features

* Player vs Computer gameplay
* Win/Loss/Draw tracking
* Match history storage
* MySQL database integration
* Input validation
* Replay option
* Player statistics dashboard

## Technologies Used

* Python
* MySQL
* mysql-connector-python
* Git & GitHub

## Project Structure

```text
Tic-Tac-Toe/
│
├── Main.py
├── database.py
├── requirements.txt
└── README.md
```

## Database Tables

### Players

Stores player statistics:

* Player Name
* Wins
* Losses
* Draws

### Matches

Stores match history:

* Match ID
* Player Name
* Result
* Date & Time

## Installation

Clone the repository:

```bash
git clone https://github.com/zamman365-glitch/Tic-Tac-Toe.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create MySQL database:

```sql
CREATE DATABASE tic_tac_toe;
```

Run the game:

```bash
python Main.py
```

## Future Improvements

* Player vs Player mode
* Leaderboard
* Match history viewer
* Move tracking
* Tkinter GUI
* Online deployment

## Author

Mohammad Zamman
