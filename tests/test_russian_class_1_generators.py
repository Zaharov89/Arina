from Arina.russian_language.class_1_tasks import generate_russian_class_1_topic_task
from Arina.russian_language.class_1_topics import RUSSIAN_CLASS_1_TOPICS


def test_russian_class_1_generates_topic_tasks():
    for topic_id in RUSSIAN_CLASS_1_TOPICS:
        for _ in range(20):
            task = generate_russian_class_1_topic_task(topic_id)
            assert task["topic"] == topic_id
            assert task["question"]
            assert "correct" in task
            assert task["answer_type"] in {"number", "choice", "text"}

            if task["answer_type"] == "choice":
                assert task["choices"]
                assert str(task["correct"]) in [str(choice) for choice in task["choices"]]


def test_russian_class_1_generator_avoids_used_question_when_possible():
    used_questions = ["Что мы слышим и произносим?"]

    for _ in range(20):
        task = generate_russian_class_1_topic_task("sounds_and_letters", used_questions=used_questions)
        assert task["question"] != "Что мы слышим и произносим?"
        assert task["is_repeat"] is False
