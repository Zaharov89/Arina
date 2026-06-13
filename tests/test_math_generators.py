from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_1_topics import CLASS_1_MATH_TOPICS
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3


def test_class_1_generates_valid_legacy_examples():
    generator = MathExamplesClass1("all", "all")

    for _ in range(50):
        example = generator.generate_example()
        answer = generator.calculate_answer(example["a"], example["op"], example["b"])
        assert answer is not None
        assert 0 <= answer <= 20


def test_class_1_generates_topic_tasks():
    for topic_id in CLASS_1_MATH_TOPICS:
        generator = MathExamplesClass1(topic_id, "all")

        for _ in range(20):
            example = generator.generate_example()
            assert example["topic"] == topic_id
            assert example["question"]
            assert "correct" in example
            assert example["answer_type"] in {"number", "choice"}

            if example["answer_type"] == "choice":
                assert example["choices"]
                assert str(example["correct"]) in [str(choice) for choice in example["choices"]]


def test_class_2_generates_valid_examples():
    generator = MathExamplesClass2("all", "all")

    for _ in range(50):
        example = generator.generate_example()
        answer = generator.calculate_answer(example["a"], example["op"], example["b"])
        assert answer is not None
        assert 0 <= answer <= 100


def test_class_3_generates_valid_examples():
    generator = MathExamplesClass3("all", "all")

    for _ in range(100):
        example = generator.generate_example()
        answer = generator.calculate_answer(example["a"], example["op"], example["b"])
        assert answer is not None
        assert 0 <= answer <= 100


def test_class_3_generates_parentheses_examples_without_crashing():
    generator = MathExamplesClass3("parentheses", "all")

    for _ in range(50):
        example = generator.generate_parentheses_example()
        assert "expr" in example
        assert isinstance(example["expr"], str)
        assert example["expr"].strip()
