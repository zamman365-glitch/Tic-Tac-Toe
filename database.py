import mysql.connector

# Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="tic_tac_toe"
)

cursor = conn.cursor()


# Add Player
def add_player(player_name):
    query = """
    INSERT IGNORE INTO players(player_name)
    VALUES (%s)
    """
    cursor.execute(query, (player_name,))
    conn.commit()


# Save Match
def save_match(player_name, result):
    query = """
    INSERT INTO matches(player_name, result)
    VALUES (%s, %s)
    """
    cursor.execute(query, (player_name, result))
    conn.commit()


# Update Win
def update_win(player_name):
    query = """
    UPDATE players
    SET wins = wins + 1
    WHERE player_name = %s
    """
    cursor.execute(query, (player_name,))
    conn.commit()


# Update Loss
def update_loss(player_name):
    query = """
    UPDATE players
    SET losses = losses + 1
    WHERE player_name = %s
    """
    cursor.execute(query, (player_name,))
    conn.commit()


# Update Draw
def update_draw(player_name):
    query = """
    UPDATE players
    SET draws = draws + 1
    WHERE player_name = %s
    """
    cursor.execute(query, (player_name,))
    conn.commit()


# Show Stats
def show_stats(player_name):
    query = """
    SELECT wins, losses, draws
    FROM players
    WHERE player_name = %s
    """

    cursor.execute(query, (player_name,))
    result = cursor.fetchone()

    if result:
        print("\nPlayer Statistics")
        print("Wins   :", result[0])
        print("Losses :", result[1])
        print("Draws  :", result[2])



def show_leaderboard():
    query = """
    SELECT player_name, wins
    FROM players
    ORDER BY wins DESC
    LIMIT 5
    """

    cursor.execute(query)

    results = cursor.fetchall()

    print("\n===== LEADERBOARD =====")

    for i, row in enumerate(results, start=1):
        print(f"{i}. {row[0]} - {row[1]} wins")

def show_match_history():
    query = """
    SELECT player_name, result, played_at
    FROM matches
    ORDER BY played_at DESC
    """

    cursor.execute(query)

    results = cursor.fetchall()

    print("\n===== MATCH HISTORY =====")

    for row in results:
        print(row)