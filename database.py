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

