from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3


def test_class_1_generates_valid_examples():
    generator = MathExamplesClass1("all", "all")

    for _ in range(50):
        example = generator.generate_example()
        answer = generator.calculate_answer(example["a"], example["op"], example["b"])
        assert answer is not None
        assert 0 <= answer <= 20


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
