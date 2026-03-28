def calculate_completion_percent(total_topics, completed_topics):
    if len(total_topics) == 0:
        return 0

    completed_count = len(set(completed_topics) & set(total_topics))
    percent = (completed_count / len(total_topics)) * 100
    return percent


def calculate_difficulty(performance_percent, completion_percent):
    difficulty = (
        (100 - performance_percent) * 0.5 +
        (100 - completion_percent) * 0.5
    )
    return round(difficulty, 2)


def calculate_priority(difficulty_score, days_remaining):
    if days_remaining <= 0:
        days_remaining = 1

    return difficulty_score / days_remaining


def get_remaining_topics(total_topics, completed_topics):
    return [topic for topic in total_topics if topic not in completed_topics]