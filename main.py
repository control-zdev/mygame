import random
import os
import json
import time
from datetime import datetime
import pwinput

# --- Utility Functions ---
def load_data():
    if not os.path.exists("names.json"):
        return {}
    with open("names.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def logstats(data):
    with open("names.json", "w") as f:
        json.dump(data, f, indent=4)

def log_challenge_result(challenger, opponent, winner, secret_number):
    with open("challenge_log.txt", "a") as f:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time_str}] {challenger} challenged {opponent}. Winner: {winner}. Number: {secret_number}\n")

def nameinput(data):
    while True:
        name = input("Enter a username to play: ").strip()
        if name:
            name = name.lower()
            if name not in data:
                print(f"Welcome {name.capitalize()}! Let's get started.")
                data[name] = {
                    "wins": 0, "losses": 0, "games": 0, "challenges_won": 0,
                    "challenges_lost": 0, "friends": [], "friend_requests": [],
                    "streak": 0, "badges": []
                }
            else:
                print(f"Welcome back {name.capitalize()}!")
            return name
        print("Username cannot be empty. Please try again.")

# --- Game Functions ---
def difficult_level(name, data):
    while True:
        print("\n_____Difficulty level_____")
        print("1. Easy\n2. Intermediate\n3. Hard\n4. Legendary\n('q' to quit)")
        print("__________________________")
        level = input("\nLevel : ").strip()
        if level == "1":
            game(10, 20, name, data)
        elif level == "2":
            game(7, 30, name, data)
        elif level == "3":
            game(5, 50, name, data)
        elif level == "4":
            game(3, 100, name, data)
        elif level.lower() == "q":
            print("\nGoodbye and thank you for playing.")
            break
        else:
            print("Invalid input! Try again.")

def offer_hint(answer, number_range):
    hint_type = random.choice(["range", "parity"])
    if hint_type == "range":
        buffer = number_range // 4
        low = max(1, answer - buffer)
        high = min(number_range, answer + buffer)
        return f"Hint: It's between {low} and {high}."
    else:
        return "Hint: It's an even number." if answer % 2 == 0 else "Hint: It's an odd number."

def update_badges(name, data):
    user = data[name]
    if user["wins"] == 1 and "First Win" not in user["badges"]:
        print("🏅 Achievement Unlocked: First Win!")
        user["badges"].append("First Win")
    if user["streak"] == 5 and "5 Wins in a Row" not in user["badges"]:
        print("🏅 Achievement Unlocked: 5 Wins in a Row!")
        user["badges"].append("5 Wins in a Row")

def game(limit, number_range, name, data):
    answer = random.randint(1, number_range)
    trial = 0
    won = False
    hint_used = False
    print(f"Enter a number (1 - {number_range}, type 'hint' for a hint.)")
    while trial < limit:
        start = time.time()
        try:
            guess_input = input(f"Entry ({limit - trial} attempts left): ")
            elapsed = time.time() - start
            if elapsed > 10:
                print("⏰ Time's up! You took too long.")
                trial += 1
                continue
            if guess_input.lower() == "hint" and not hint_used:
                print(offer_hint(answer, number_range))
                hint_used = True
                continue
            num = int(guess_input)
            trial += 1
            if num == answer:
                print(f"🎉Congrats! 🎉 You got it in {trial} attempts.😊")
                data[name]["wins"] += 1
                data[name]["streak"] += 1
                update_badges(name, data)
                won = True
                break
            elif num < answer:
                print("Very close! A bit higher." if num == answer - 1 else "Too low!")
            else:
                print("Very close! A bit lower." if num == answer + 1 else "Too high.")
        except ValueError:
            print("Must enter a valid integer or type 'hint' once!")
    if not won:
        print(f"Out of attempts! Correct number was {answer}.")
        data[name]["losses"] += 1
        data[name]["streak"] = 0

    data[name]["games"] += 1
    viewstats(name, data)

# --- Stats Function ---
def viewstats(name, data):
    stats = data[name]
    win_rate = (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0
    print(f"\n--- Stats for {name.capitalize()} ---")
    print(f"Games played: {stats['games']}")
    print(f"Wins: {stats['wins']} | Losses: {stats['losses']} | Win Rate: {win_rate:.2f}%")
    print(f"Challenges Won: {stats.get('challenges_won', 0)} | Challenges Lost: {stats.get('challenges_lost', 0)}")
    print(f"Current Win Streak: {stats.get('streak', 0)}")
    print(f"Badges: {', '.join(stats.get('badges', [])) if stats.get('badges') else 'None'}")


def play_challenge_round(player_name, answer, limit, number_range, data):
    trial = 0
    guess = None
    hint_used = False
    print(f"{player_name.capitalize()}, you have {limit} attempts. Type 'hint' once if needed. You have 10 seconds per guess.")
    while trial < limit:
        start = time.time()
        try:
            guess_input = pwinput.pwinput(prompt=f"{player_name.capitalize()}'s Guess ({limit - trial} left): ")
            elapsed = time.time() - start
            if elapsed > 10:
                print("⏰ Time's up! You took too long.")
                trial += 1
                continue
            if guess_input.lower() == "hint" and not hint_used:
                print(offer_hint(answer, number_range))
                hint_used = True
                continue
            guess = int(guess_input)
            trial += 1
            if guess == answer:
                print(f"🎯 Correct! You got it in {trial} attempts.")
                data[player_name]["wins"] += 1
                return trial
            elif guess < answer:
                print("Too low!")
            else:
                print("Too high!")
        except ValueError:
            print("Invalid input. Try again.")
    print(f"😢 {player_name.capitalize()} couldn't guess it. The answer was hidden.")
    data[player_name]["losses"] += 1
    return limit + 1

def challenge_friend(name, data):
    friends = data[name].get("friends", [])
    if not friends:
        print(f"{name.capitalize()} has no friends to challenge.")
        return

    print("\n--- Challenge a Friend ---")
    for idx, friend in enumerate(friends, start=1):
        print(f"{idx}. {friend.capitalize()}")
    try:
        choice = int(input("Choose a friend to challenge (number): "))
        if 1 <= choice <= len(friends):
            friend_name = friends[choice - 1]
            number_range = 30
            limit = 5
            secret_number = random.randint(1, number_range)

            print(f"\n{name.capitalize()}, it's your turn to guess (1 - {secret_number}):")
            user_attempts = play_challenge_round(name, secret_number, limit, number_range, data)
            input("Press Enter to pass to your friend...")
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"\n{friend_name.capitalize()}, it's your turn to guess:")
            friend_attempts = play_challenge_round(friend_name, secret_number, limit, number_range, data)

            if user_attempts < friend_attempts:
                print(f"\n🏆 {name.capitalize()} wins the challenge!")
                data[name]["challenges_won"] += 1
                data[friend_name]["challenges_lost"] += 1
                winner = name
            elif friend_attempts < user_attempts:
                print(f"\n🏆 {friend_name.capitalize()} wins the challenge!")
                data[friend_name]["challenges_won"] += 1
                data[name]["challenges_lost"] += 1
                winner = friend_name
            else:
                print("\nIt's a tie!")
                winner = "Tie"

            log_challenge_result(name, friend_name, winner, secret_number)
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# --- Leaderboard ---
def leaderboard(data):
    print("\n--- Leaderboard ---")
    ranked = sorted(data.items(), key=lambda x: x[1].get("wins", 0), reverse=True)
    for i, (player, stats) in enumerate(ranked, 1):
        win_rate = (stats['wins'] / stats['games'] * 100) if stats['games'] else 0
        print(f"{i}. {player.capitalize()} - Wins: {stats['wins']}, Games: {stats['games']}, Win Rate: {win_rate:.2f}%")

# --- Friend Management ---
def add_friend(name, data):
    friend_name = input("Enter the username to send a friend request: ").strip().lower()
    if friend_name == name:
        print("You can't add yourself.")
        return
    if friend_name in data:
        if name not in data[friend_name].get("friend_requests", []):
            data[friend_name].setdefault("friend_requests", []).append(name)
            print(f"Friend request sent to {friend_name.capitalize()}.")
        else:
            print("Request already sent.")
    else:
        print("That user doesn't exist.")

def view_friend_requests(name, data):
    requests = data[name].get("friend_requests", [])
    if not requests:
        print("No friend requests.")
        return
    print("\n--- Pending Friend Requests ---")
    for idx, r in enumerate(requests, start=1):
        print(f"{idx}. {r.capitalize()}")
    try:
        choice = int(input("Accept which request (number)? 0 to ignore: "))
        if choice == 0:
            return
        selected = requests[choice - 1]
        data[name].setdefault("friends", []).append(selected)
        data[selected].setdefault("friends", []).append(name)
        data[name]["friend_requests"].remove(selected)
        print(f"You and {selected.capitalize()} are now friends!")
    except (ValueError, IndexError):
        print("Invalid choice.")

def view_friends(name, data):
    friends = data[name].get("friends", [])
    if not friends:
        print("No friends added yet.")
    else:
        print(f"\n--- Friends of {name.capitalize()} ---")
        for f in friends:
            print(f.capitalize())

# --- Main Menu ---
def main_menu(data, name):
    while True:
        print("\n--- Main Menu ---")
        print("1. Play Game")
        print("2. View Stats")
        print("3. Add Friend")
        print("4. View Friend Requests")
        print("5. View Friends")
        print("6. Challenge Friend")
        print("7. View Leaderboard")
        print("8. How to play (help).")
        print("'q' to Quit")
        print("_________________")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            difficult_level(name, data)
        elif choice == "2":
            viewstats(name, data)
        elif choice == "3":
            add_friend(name, data)
        elif choice == "4":
            view_friend_requests(name, data)
        elif choice == "5":
            view_friends(name, data)
        elif choice == "6":
            challenge_friend(name, data)
        elif choice == "7":
            leaderboard(data)
        elif choice.lower() == "8":
            explain_game()
        elif choice.lower() == "q":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

#game manual
def explain_game():
    print("\n🎮 --- Welcome to the Number Challenge Game! --- 🎮")
    print("""
This is a number guessing game with extra features for fun and competition.

🔢 GAMEPLAY:
- You'll guess a number between a random range based on difficulty.
- You have a limited number of attempts.
- Type 'hint' once per game to get help.
- You have 10 seconds for each guess!

💥 DIFFICULTY LEVELS:
1. Easy       - 10 tries, numbers between 1-20
2. Intermediate - 7 tries, numbers between 1-30
3. Hard       - 5 tries, numbers between 1-50
4. Legendary  - 3 tries, numbers between 1-100

🎯 STATS & BADGES:
- Your wins, losses, win rate, and streaks are recorded.
- Badges like “First Win” and “5 Wins in a Row” are awarded automatically.

🤝 FRIEND SYSTEM:
- Send and accept friend requests.
- You can only challenge people who have accepted your request.

⚔️ CHALLENGE FRIEND:
- Both players guess the same secret number, one at a time.
- The player cannot see the answer until the challenge round ends.
- The better guesser wins the challenge by least tries used.

🏆 LEADERBOARD:
- Shows top players based on wins and win rate.

💡 TIPS:
- Use your hints wisely.
- The timer adds pressure, so think fast!
- Build streaks and collect all the badges.

Ready to prove you're the number master? Let's play! 😉
    """)

# --- Main Execution ---
def main():
    data = load_data()
    name = nameinput(data)
    main_menu(data, name)
    logstats(data)

if __name__ == "__main__":
    main()