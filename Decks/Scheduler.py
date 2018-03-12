import enum
from datetime import timedelta

class AnswerDifficulty(enum.Enum):
    easy = 5
    medium = 4
    hard = 3
    incorrect = 1


class Scheduler(object):
    def __calculate_easing_factor(self, card, difficulty):
        new_ef = card.easing_factor - 0.8 + 0.28*difficulty - 0.02*difficulty*difficulty
        if new_ef < 1.3:
            new_ef = 1.3
        card.easing_factor = new_ef

    def __schedule_card(self, card, base_time):
        interval = None
        if card.level == 1:
            interval = timedelta(days=1)
        elif card.level == 2:
            interval = timedelta(days=4)
        else:
            interval = card.current_interval * card.easing_factor

        card.due_time = base_time + interval
        card.current_interval = interval
        card.level += 1

    def answer(self, card, base_time, difficulty):
        self.__calculate_easing_factor(card, difficulty)

        if difficulty == AnswerDifficulty.incorrect:
            card.level = 1

        self.__schedule_card(card, base_time)