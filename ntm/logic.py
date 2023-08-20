import random
from ntm.schema import Game, Question
from ntm.config import GAME_LENGTH


def create_assortment_of_questions(session):
    questions = list(session.query(Question).all())
    questions_dict = [
        {
            "filename": question.filename,
            "options": (
                random.sample(
                    [
                        question.correct_option,
                        question.false_option1,
                        question.false_option2,
                        question.false_option3,
                    ],
                    4,
                )
                if "final" not in question.filename
                else [
                    question.false_option1,
                    question.false_option2,
                    question.false_option3,
                    question.correct_option,
                ]
            ),
        }
        for question in questions
    ]
    random.shuffle(questions_dict)

    final_pos = 0
    for i in range(len(questions_dict)):
        if "final" in questions_dict[i]["filename"]:
            final_pos = i
            break
    
    final_question = questions_dict[final_pos]
    if final_pos != len(questions_dict) - 1:
        questions_dict = questions_dict[:final_pos] + questions_dict[final_pos + 1 :]

    questions_dict[GAME_LENGTH - 1] = final_question
    return questions_dict[:GAME_LENGTH]


def make_new_game(email: str, session) -> Game:
    game = Game(user_email=email)
    session.add(game)
    session.commit()
    return game


def is_answer_right(question_id: str, answer: str, session) -> bool:
    question = session.query(Question).filter(Question.id == question_id)
    return question.correct_option == answer
