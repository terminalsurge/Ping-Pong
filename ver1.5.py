import pygame
import mysql.connector
username = None
rect_change_x = 0
rect_x = 400  # initial position
# Database setup
conn = mysql.connector.connect(
    user='root',
    password='mysql',
    host='localhost',
    database='mydb'
)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN (
        NAME VARCHAR(20) NOT NULL,
        PASSWORD VARCHAR(255) NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS HIGHSCORE (
        NAME VARCHAR(20),
        SCORE INT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS leaderboard (
        NAME VARCHAR(30),
        SCORE INT
    )
''')

# Game setup
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

size = (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pong")

# Paddle setup
rect_x = 400
rect_y = 580
rect_change_x = 0

# Ball setup
ball_x = 50
ball_y = 50
ball_change_x = 5
ball_change_y = 5

score = 0

# Functions to draw paddle and handle movement restrictions
def drawrect(screen, x, y):
    if x <= 0:
        x = 0
    if x >= 699:
        x = 699
    pygame.draw.rect(screen, RED, [x, y, 100, 20])

# Main menu
def main_menu():
    while True:
        print("\nOptions:")
        print("1. Login")
        print("2. Create Account")
        print("3. Play Game")
        print("4. View Leaderboard")
        print("5. Exit")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            login()
        elif choice == "2":
            create_account()
        elif choice == "3":
            play_game()
        elif choice == "4":
            view_leaderboard()
        elif choice == "5":
            exit_game()
        else:
            print("Invalid choice. Please try again.")

def login():
    global username
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute("SELECT * FROM LOGIN WHERE NAME = %s AND PASSWORD = %s", (username, password))
    if cursor.fetchone():
        print("Login successful!")
    else:
        print("Invalid login credentials. Please try again.")
        username = None

def create_account():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    cursor.execute("INSERT INTO LOGIN (NAME, PASSWORD) VALUES (%s, %s)", (username, password))
    conn.commit()
    print("Account created successfully!")

def play_game():
    global score
    global rect_x, rect_change_x, ball_x, ball_y, ball_change_x, ball_change_y
    done = False
    clock = pygame.time.Clock()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rect_change_x = -6
                elif event.key == pygame.K_RIGHT:
                    rect_change_x = 6
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    rect_change_x = 0

        screen.fill(BLACK)
        rect_x += rect_change_x

        ball_x += ball_change_x
        ball_y += ball_change_y

        # Ball collision logic
        if ball_x < 0 or ball_x > 785:
            ball_change_x *= -1
        if ball_y < 0:
            ball_change_y *= -1
        elif rect_x < ball_x < rect_x + 100 and ball_y >= 560:
            ball_change_y *= -1
            score += 1
        elif ball_y > 600:
            ball_y = 50
            ball_x = 50
            ball_change_x *= -1
            ball_change_y *= -1
            score = 0  # Reset score on miss

        pygame.draw.rect(screen, WHITE, [ball_x, ball_y, 15, 15])
        drawrect(screen, rect_x, rect_y)

        # Scoreboard
        font = pygame.font.SysFont('Calibri', 20, False, False)
        text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(text, [10, 10])

        pygame.display.flip()
        clock.tick(60)

    # Save score to leaderboard
    cursor.execute("SELECT SCORE FROM leaderboard WHERE NAME = %s", (username,))
    existing_score = cursor.fetchone()
    if not existing_score or score > existing_score[0]:
        cursor.execute("REPLACE INTO leaderboard (NAME, SCORE) VALUES (%s, %s)", (username, score))
        conn.commit()

def view_leaderboard():
    cursor.execute("SELECT * FROM leaderboard ORDER BY SCORE DESC")
    print("\nLeaderboard:")
    for rank, (name, score) in enumerate(cursor.fetchall(), start=1):
      print(f"{rank}. {name} - {score}")

def exit_game():
    cursor.close()
    conn.close()
    pygame.quit()
    quit()

# Start the program
username = None
main_menu()
