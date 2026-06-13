from Arina.world.class_1_tasks import generate_world_class_1_topic_task
from Arina.world.class_1_topics import WORLD_CLASS_1_TOPICS


def test_world_class_1_generates_topic_tasks():
    for topic_id in WORLD_CLASS_1_TOPICS:
        for _ in range(20):
            task = generate_world_class_1_topic_task(topic_id)
            assert task["topic"] == topic_id
            assert task["question"]
            assert "correct" in task
            assert task["answer_type"] in {"number", "choice", "text"}

            if task["answer_type"] == "choice":
                assert task["choices"]
                assert str(task["correct"]) in [str(choice) for choice in task["choices"]]


def test_world_class_1_generator_avoids_used_question_when_possible():
    used_questions = ["Что относится к живой природе?"]

    for _ in range(20):
        task = generate_world_class_1_topic_task("living_nonliving", used_questions=used_questions)
        assert task["question"] != "Что относится к живой природе?"
        assert task["is_repeat"] is False
