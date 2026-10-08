"""
Лабораторная работа № 6. Вариант 12: Итоговая оценка.
"""

from typing import Protocol, List, Tuple
import unittest


# --- Контракт (Интерфейс) ---

class GradingPolicy(Protocol):
    def calculate(self, scores: List[float]) -> Tuple[float, str]:
        """Возвращает (итоговый_балл, статус)."""
        ...


# --- Реализации компонентов ---

class WeightedPolicy:
    """Взвешенная политика: ранние оценки имеют меньший вес, последняя — максимальный."""
    def calculate(self, scores: List[float]) -> Tuple[float, str]:
        if not scores:
            return 0.0, "нет данных"
        weights = [i + 1 for i in range(len(scores))]
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        final_score = weighted_sum / sum(weights)
        status = "сдан" if final_score >= 50 else "не сдан"
        return round(final_score, 2), status


class BestAttemptPolicy:
    """Политика лучшей попытки: берется максимальный балл."""
    def calculate(self, scores: List[float]) -> Tuple[float, str]:
        if not scores:
            return 0.0, "нет данных"
        final_score = max(scores)
        status = "сдан" if final_score >= 50 else "не сдан"
        return round(final_score, 2), status


class PassFailPolicy:
    """Политика Зачет/Незачет: средний балл, но строго порог 60."""
    def calculate(self, scores: List[float]) -> Tuple[float, str]:
        if not scores:
            return 0.0, "нет данных"
        final_score = sum(scores) / len(scores)
        status = "зачтено" if final_score >= 60 else "не зачтено"
        return round(final_score, 2), status


class MemoryPolicy:
    """Тестовый дублёр для проверки вызовов стратегии в памяти."""
    def __init__(self):
        self.last_scores: List[float] = []

    def calculate(self, scores: List[float]) -> Tuple[float, str]:
        self.last_scores = list(scores)
        return 100.0, "тест"


# --- Бизнес-логика ---

class Student:
    def __init__(self, student_id: int, name: str):
        if isinstance(student_id, bool) or not isinstance(student_id, int):
            raise TypeError("Идентификатор должен быть целым числом")
        if student_id <= 0 or not isinstance(name, str) or not name.strip():
            raise ValueError("Некорректные данные студента")

        self.student_id = student_id
        self.name = name.strip()
        self.scores: List[float] = []

    def add_score(self, score: float) -> None:
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("Балл должен быть числом")
        if not 0 <= score <= 100:
            raise ValueError("Балл должен быть от 0 до 100")
        self.scores.append(float(score))


class GradeCalculator:
    def __init__(self, policy: GradingPolicy):
        self._students: dict[int, Student] = {}
        self._policy = policy  # Композиция

    def register(self, student: Student) -> None:
        if student.student_id in self._students:
            raise ValueError("Студент уже зарегистрирован")
        self._students[student.student_id] = student

    def add_score(self, student_id: int, score: float) -> None:
        self._get_student(student_id).add_score(score)

    def compute_grade(self, student_id: int) -> Tuple[float, str]:
        student = self._get_student(student_id)
        return self._policy.calculate(student.scores)

    def _get_student(self, student_id: int) -> Student:
        try:
            return self._students[student_id]
        except KeyError as error:
            raise KeyError("Студент не найден") from error


# --- Демонстрационный запуск ---

def main():
    print("--- WeightedPolicy ---")
    calc_weighted = GradeCalculator(WeightedPolicy())
    calc_weighted.register(Student(1, "Алихан"))
    calc_weighted.add_score(1, 40)
    calc_weighted.add_score(1, 80)  # Вес последней оценки выше
    print("Итог:", calc_weighted.compute_grade(1))

    print("\n--- BestAttemptPolicy ---")
    calc_best = GradeCalculator(BestAttemptPolicy())
    calc_best.register(Student(1, "Алихан"))
    calc_best.add_score(1, 40)
    calc_best.add_score(1, 80)
    print("Итог:", calc_best.compute_grade(1))


# --- Тесты ---

class TestGradeCalculator(unittest.TestCase):
    def test_weighted_policy_calculation(self):
        calc = GradeCalculator(WeightedPolicy())
        calc.register(Student(1, "Amina"))
        calc.add_score(1, 50)
        calc.add_score(1, 100)  # (50*1 + 100*2) / 3 = 83.33
        score, status = calc.compute_grade(1)
        self.assertEqual(score, 83.33)
        self.assertEqual(status, "сдан")

    def test_interchangeability_pass_fail_policy(self):
        calc = GradeCalculator(PassFailPolicy())
        calc.register(Student(1, "Amina"))
        calc.add_score(1, 55)
        score, status = calc.compute_grade(1)
        self.assertEqual(status, "не зачтено")

    def test_memory_policy_injection(self):
        policy = MemoryPolicy()
        calc = GradeCalculator(policy)
        calc.register(Student(1, "Amina"))
        calc.add_score(1, 90)
        calc.compute_grade(1)
        self.assertEqual(policy.last_scores, [90.0])

    def test_error_unknown_student(self):
        calc = GradeCalculator(MemoryPolicy())
        with self.assertRaisesRegex(KeyError, "Студент не найден"):
            calc.compute_grade(999)

    def test_error_invalid_score(self):
        student = Student(1, "Arman")
        with self.assertRaisesRegex(ValueError, "Балл должен быть от 0 до 100"):
            student.add_score(150)

    def test_error_invalid_student_id_type(self):
        with self.assertRaisesRegex(TypeError, "Идентификатор должен быть целым числом"):
            Student(True, "Arman")


if __name__ == "__main__":
    main()
    print("\n--- Running Unit Tests ---")
    unittest.main(exit=False)