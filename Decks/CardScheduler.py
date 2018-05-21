import enum
from datetime import timedelta, datetime

class AnswerDifficulty(enum.Enum):
    easy = 5
    medium = 4
    hard = 3
    incorrect = 1

def string_to_difficulty(s:str):
    d = {'easy':AnswerDifficulty.easy,
         'medium':AnswerDifficulty.medium,
         'hard':AnswerDifficulty.hard,
         'incorrect':AnswerDifficulty.incorrect}

    return d.get(s.strip(' ').lower(), None)


class CardScheduler(object):
    def __calculate_easing_factor(self, card, difficulty):
        new_ef = card.easing_factor - 0.8 + 0.28*difficulty - 0.02*difficulty*difficulty
        if new_ef < 1.3:
            new_ef = 1.3
        card.easing_factor = new_ef

    def __schedule_card(self, card, base_time):
        interval = None
        if card.level == 1:
            interval = timedelta(days=1).total_seconds()
        elif card.level == 2:
            interval = timedelta(days=4).total_seconds()
        else:
            epoch = datetime.utcfromtimestamp(0)
            interval = (card.current_interval - epoch).total_seconds() * card.easing_factor

        card.due_time = base_time + timedelta(seconds=interval)

        card.current_interval = datetime.utcfromtimestamp(interval)
        card.level += 1
        card.learned = True

    def answer(self, card, base_time, difficulty):
        self.__calculate_easing_factor(card, difficulty)

        if difficulty == AnswerDifficulty.incorrect:
            card.level = 1

        self.__schedule_card(card, base_time)