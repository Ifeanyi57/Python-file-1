import random
import re
import json
import os
import time
from colorama import init, Fore, Style

init(autoreset=True)

COLOR_GREEN = Fore.GREEN
COLOR_YELLOW = Fore.YELLOW
COLOR_RED = Fore.RED
COLOR_BLUE = Fore.BLUE
COLOR_END = Style.RESET_ALL  # Define COLOR_END

MATRIC_LENGTH = 6  # Renamed for clarity
# Initialize a dictionary to store scores for each category
category_scores = {}
# Initialize a set to track completed categories
completed_categories = set()

SCORE_FILE = "scores.json"
QUESTION_FILE = "questions.json"

def load_scores():
    """Load existing scores from file."""
    scores = {}
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                scores = json.load(f)
                print("Loaded previous scores.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {SCORE_FILE}. Starting with an empty score history.")
        except Exception as e:
            print(f"An error occurred while loading scores: {e}")
    return scores

def save_scores(scores):
    """Save scores to file."""
    try:
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f, indent=4)
        print(f"Scores saved to {SCORE_FILE}")
    except Exception as e:
        print(f"An error occurred while saving the score: {e}")

def load_question_bank():
    """Load question bank from JSON file."""
    try:
        with open(QUESTION_FILE, "r") as f:
            question_bank = json.load(f)
        print("Loaded question bank.")
        return question_bank
    except FileNotFoundError:
        print(f"Error: {QUESTION_FILE} not found. Please ensure the file exists.")
        return None # Return None to indicate failure
    except json.JSONDecodeError:
        print(f"Error: {QUESTION_FILE} is corrupted or invalid JSON.")
        print("Please check the file format.")
        return None # Return None to indicate failure
    except Exception as e:
        print(f"An error occurred while loading questions: {e}")
        return None # Return None to indicate failure

def validate_name(name):
    """Validate student name."""
    if not name.strip():
        return False, "Name cannot be empty."
    if not re.match("^[A-Za-z\s'-]+$", name): #Check if name contains only letters, spaces, apostrophes, or hyphens
        return False, "Error. Input a valid name."
    return True, ""

def validate_matric(matric):
    """Validate matric number."""
    if not matric.strip():
        return False, "Matric number cannot be empty."
    if len(matric) != MATRIC_LENGTH:
        return False, f"Error. Your matric number is too short. It must be {MATRIC_LENGTH} characters long."
    if not matric.isalnum(): #Allow alphanumeric characters
        return False, "Error. Matric number should contain only alphanumeric characters."
    return True, ""

def get_student_info():
    """Prompt and validate student name and matric number."""
    while True:
        student_name = input("Enter your name: ")
        is_valid_name, name_error = validate_name(student_name)
        if not is_valid_name:
            print(name_error)
            continue

        student_matric = input("Enter your matric number: ")
        is_valid_matric, matric_error = validate_matric(student_matric)
        if not is_valid_matric:
            print(matric_error)
            continue

        print(f"{COLOR_GREEN}Welcome {student_name}, your matric number is {student_matric}.{COLOR_END}")
        print(f"{COLOR_BLUE}Let's start the examination. No side talks please.{COLOR_END}")
        return student_name, student_matric # Exit the loop when all conditions are met

def run_category_quiz(category, questions, category_scores, completed_categories):
    """Runs the quiz for a specific category."""
    print(f"\nStarting quiz for category: {category}")
    # Reset score for the category if it's being retaken
    if category in completed_categories:
        category_scores[category] = 0
    else:
        # Initialize score for a new category
        category_scores[category] = 0

    random.shuffle(questions)

    for i, qa in enumerate(questions, 1):
        if not isinstance(qa, dict) or 'question' not in qa or 'answer' not in qa:
             print(f"{COLOR_RED}Skipping invalid question format in category '{category}': {qa}{COLOR_END}")
             continue # Skip this item if it's not a valid question dictionary

        user_answer = input(f"Question {i}: {qa['question']}").strip().lower()
        if user_answer == qa["answer"].lower(): # Compare lowercased answers
            print("Correct!")
            category_scores[category] += 1
        else:
            print(f"Incorrect. The correct answer is: {qa['answer']}")

    print(f"{COLOR_YELLOW}Finished examination for {category}. Your score for this category is {category_scores[category]}/{len(questions)}.{COLOR_END}")

    # Add the category to the set of completed categories
    completed_categories.add(category)


def main():
    print("Welcome! Ready for your first examination")

    scores = load_scores()
    question_bank = load_question_bank()

    if question_bank is None:
        # Exit if question bank failed to load
        return

    category_scores = {}
    completed_categories = set()
    total_questions = sum(len(q) for q in question_bank.values())
    # Calculate PASSING_SCORE as 70% of total questions
    PASSING_SCORE = int(total_questions * 0.70)
    print(f"The passing score for this examination is: {PASSING_SCORE}/{total_questions}")

    student_name, student_matric = get_student_info()

    while True:
        print(f"\nAvailable categories: {list(question_bank.keys())}")
        category_choice = input(f"Choose a category: ").strip().capitalize()

        if category_choice in question_bank:
            run_category_quiz(category_choice, question_bank[category_choice], category_scores, completed_categories)
        else:
            print("Invalid category.")

        retry = input(f"{COLOR_BLUE}Do you want to try another category? (yes/no): {COLOR_END}").lower()
        if retry != 'yes':
            break # Exit the category loop if the user doesn't want to retry

    # Calculate and display overall score and percentage after exiting the loop
    overall_score = sum(category_scores.values())
    overall_percentage = (overall_score / total_questions) * 100 if total_questions > 0 else 0 # Avoid division by zero
    print(f"{COLOR_GREEN}\nOverall Examination Results:{COLOR_END}")
    print(f"{COLOR_GREEN}Your total score is {overall_score}/{total_questions} ({overall_percentage:.2f}%).{COLOR_END}")
    if overall_score < PASSING_SCORE:
        print(f"{COLOR_RED}You failed the examination. Better luck next time.{COLOR_END}")
    else:
        print(f"{COLOR_GREEN}Congratulations! You passed the examination.{COLOR_END}")

    # Save the score after the overall score is calculated
    scores[student_matric] = {"name": student_name, "score": overall_score, "date": time.strftime("%Y-%m-%d"), "categories": category_scores} # Include category scores
    save_scores(scores)


if __name__ == "__main__":
    main()