#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Mentor System Tests
Test MENTOR//NODE NetworkChuck-style education curriculum
"""

import pytest
from unittest.mock import Mock, patch
from core.modules.mentor_system import MentorSystem, LessonProgress


class TestMentorSystem:
    """Test MentorSystem education curriculum"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system with temp progress file"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_initial_progress(self, mentor):
        """Test that initial progress is Lesson 1.1"""
        progress = mentor.get_progress()

        assert progress["current_chapter"] == 1
        assert progress["current_lesson"] == 1
        assert progress["completed_lessons"] == 0

    def test_get_current_lesson(self, mentor):
        """Test getting current lesson content"""
        lesson = mentor.get_current_lesson()

        assert lesson["chapter"] == 1
        assert lesson["lesson"] == 1
        assert "title" in lesson
        assert "content" in lesson
        assert "key_points" in lesson

    def test_lesson_1_1_content(self, mentor):
        """Test Lesson 1.1: The Two-Timeframe Philosophy"""
        lesson = mentor.get_lesson(chapter=1, lesson=1)

        assert "Two-Timeframe" in lesson["title"]
        assert "4H" in lesson["content"] or "15M" in lesson["content"]
        assert len(lesson["key_points"]) > 0

    def test_complete_lesson(self, mentor):
        """Test completing a lesson"""
        # Complete Lesson 1.1
        result = mentor.complete_lesson(chapter=1, lesson=1)

        assert result["success"] is True
        assert result["next_lesson"] == {"chapter": 1, "lesson": 2}

        # Verify progress updated
        progress = mentor.get_progress()
        assert progress["completed_lessons"] == 1
        assert progress["current_lesson"] == 2

    def test_complete_quiz(self, mentor):
        """Test completing a quiz"""
        # Get quiz for Lesson 1.1
        quiz = mentor.get_quiz(chapter=1, lesson=1)

        assert "questions" in quiz
        assert len(quiz["questions"]) > 0

        # Submit correct answers
        answers = {
            "q1": "4H for structure, 15M for entry",
            "q2": "Both timeframes must confirm",
            "q3": "1-2% risk per trade"
        }

        result = mentor.submit_quiz(chapter=1, lesson=1, answers=answers)

        assert result["passed"] is True
        assert result["score"] >= 70  # Passing score

    def test_quiz_failure(self, mentor):
        """Test quiz failure with wrong answers"""
        # Get quiz for Lesson 1.1
        quiz = mentor.get_quiz(chapter=1, lesson=1)

        # Submit wrong answers
        answers = {
            "q1": "wrong answer",
            "q2": "wrong answer",
            "q3": "wrong answer"
        }

        result = mentor.submit_quiz(chapter=1, lesson=1, answers=answers)

        assert result["passed"] is False
        assert result["score"] < 70

    def test_lesson_progression(self, mentor):
        """Test progressing through lessons"""
        # Complete Lesson 1.1
        mentor.complete_lesson(1, 1)
        progress = mentor.get_progress()
        assert progress["current_lesson"] == 2

        # Complete Lesson 1.2
        mentor.complete_lesson(1, 2)
        progress = mentor.get_progress()
        assert progress["current_lesson"] == 3

        # Complete Lesson 1.3
        mentor.complete_lesson(1, 3)
        progress = mentor.get_progress()
        assert progress["current_lesson"] == 4

    def test_chapter_completion(self, mentor):
        """Test completing all lessons in a chapter"""
        # Complete all 6 lessons in Chapter 1
        for lesson_num in range(1, 7):
            mentor.complete_lesson(1, lesson_num)

        progress = mentor.get_progress()

        # Should advance to Chapter 2
        assert progress["current_chapter"] == 2
        assert progress["current_lesson"] == 1
        assert progress["completed_lessons"] == 6


class TestLessonContent:
    """Test lesson content and structure"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_chapter_1_lessons(self, mentor):
        """Test that Chapter 1 has all 6 lessons"""
        lessons = mentor.get_chapter_lessons(chapter=1)

        assert len(lessons) == 6

        # Verify lesson titles
        expected_titles = [
            "Two-Timeframe Philosophy",
            "4H Chart: Market Structure",
            "15M Chart: Entry Timing",
            "1-2% Risk Rule",
            "Position Sizing Formula",
            "The 3-Strike Rule"
        ]

        for i, lesson in enumerate(lessons):
            assert any(title_part in lesson["title"] for title_part in expected_titles[i].split())

    def test_lesson_key_points(self, mentor):
        """Test that lessons have key points"""
        for lesson_num in range(1, 7):
            lesson = mentor.get_lesson(chapter=1, lesson=lesson_num)

            assert "key_points" in lesson
            assert len(lesson["key_points"]) >= 3
            assert all(isinstance(point, str) for point in lesson["key_points"])

    def test_lesson_examples(self, mentor):
        """Test that lessons have examples"""
        for lesson_num in range(1, 7):
            lesson = mentor.get_lesson(chapter=1, lesson=lesson_num)

            assert "examples" in lesson or "example" in lesson["content"].lower()


class TestQuizzes:
    """Test quiz functionality"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_quiz_structure(self, mentor):
        """Test quiz structure"""
        quiz = mentor.get_quiz(chapter=1, lesson=1)

        assert "questions" in quiz
        assert "passing_score" in quiz

        for question in quiz["questions"]:
            assert "id" in question
            assert "question" in question
            assert "options" in question or "type" in question

    def test_quiz_scoring(self, mentor):
        """Test quiz scoring calculation"""
        quiz = mentor.get_quiz(chapter=1, lesson=1)
        total_questions = len(quiz["questions"])

        # Correct half the questions
        answers = {}
        for i, q in enumerate(quiz["questions"]):
            if i < total_questions // 2:
                answers[q["id"]] = q["correct_answer"]
            else:
                answers[q["id"]] = "wrong answer"

        result = mentor.submit_quiz(chapter=1, lesson=1, answers=answers)

        # Score should be around 50%
        assert 40 <= result["score"] <= 60

    def test_quiz_retake(self, mentor):
        """Test retaking a failed quiz"""
        # Fail first attempt
        wrong_answers = {
            "q1": "wrong",
            "q2": "wrong",
            "q3": "wrong"
        }
        result1 = mentor.submit_quiz(1, 1, wrong_answers)
        assert result1["passed"] is False

        # Pass second attempt
        quiz = mentor.get_quiz(chapter=1, lesson=1)
        correct_answers = {q["id"]: q["correct_answer"] for q in quiz["questions"]}
        result2 = mentor.submit_quiz(1, 1, correct_answers)
        assert result2["passed"] is True


class TestProgressTracking:
    """Test progress tracking and statistics"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_completion_percentage(self, mentor):
        """Test calculating completion percentage"""
        # Complete 3 out of 6 lessons in Chapter 1
        for lesson_num in range(1, 4):
            mentor.complete_lesson(1, lesson_num)

        progress = mentor.get_progress()

        # 3/42 total lessons = ~7%
        assert progress["completion_percent"] >= 7
        assert progress["completion_percent"] <= 8

    def test_track_quiz_attempts(self, mentor):
        """Test tracking quiz attempts"""
        # Take quiz 3 times
        for _ in range(3):
            mentor.submit_quiz(chapter=1, lesson=1, {"q1": "wrong"})

        progress = mentor.get_progress()
        lesson_stats = progress["lesson_stats"]["1.1"]

        assert lesson_stats["quiz_attempts"] == 3

    def test_track_time_spent(self, mentor):
        """Test tracking time spent on lessons"""
        # Start lesson
        mentor.start_lesson(chapter=1, lesson=1)

        # Simulate time passing
        import time
        time.sleep(1)

        # Complete lesson
        mentor.complete_lesson(chapter=1, lesson=1)

        progress = mentor.get_progress()
        lesson_stats = progress["lesson_stats"]["1.1"]

        assert lesson_stats["time_spent"] > 0


@pytest.mark.unit
class TestMentorIntegration:
    """Integration tests for mentor system"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_complete_lesson_workflow(self, mentor):
        """Test complete lesson workflow"""
        # Step 1: Get lesson
        lesson = mentor.get_current_lesson()
        assert lesson["chapter"] == 1
        assert lesson["lesson"] == 1

        # Step 2: Read content
        assert len(lesson["content"]) > 0

        # Step 3: Take quiz
        quiz = mentor.get_quiz(chapter=1, lesson=1)
        correct_answers = {q["id"]: q["correct_answer"] for q in quiz["questions"]}

        # Step 4: Submit quiz
        result = mentor.submit_quiz(chapter=1, lesson=1, correct_answers)
        assert result["passed"] is True

        # Step 5: Complete lesson
        completion = mentor.complete_lesson(chapter=1, lesson=1)
        assert completion["success"] is True

        # Step 6: Verify progress
        progress = mentor.get_progress()
        assert progress["current_lesson"] == 2

    def test_progress_persistence(self, tmp_path):
        """Test that progress persists across sessions"""
        progress_file = tmp_path / "lesson_progress.json"

        # Session 1: Complete 2 lessons
        mentor1 = MentorSystem(progress_file=str(progress_file))
        mentor1.complete_lesson(1, 1)
        mentor1.complete_lesson(1, 2)

        # Session 2: Load progress
        mentor2 = MentorSystem(progress_file=str(progress_file))
        progress = mentor2.get_progress()

        # Should remember completed lessons
        assert progress["completed_lessons"] == 2
        assert progress["current_lesson"] == 3


class TestNetworkChuckStyle:
    """Test NetworkChuck teaching style elements"""

    @pytest.fixture
    def mentor(self, tmp_path):
        """Create mentor system"""
        progress_file = tmp_path / "lesson_progress.json"
        return MentorSystem(progress_file=str(progress_file))

    def test_engaging_content(self, mentor):
        """Test that content is engaging and practical"""
        lesson = mentor.get_lesson(chapter=1, lesson=1)

        # Should have practical examples
        content_lower = lesson["content"].lower()
        assert any(keyword in content_lower for keyword in [
            "example", "real", "actual", "practice", "let's"
        ])

    def test_visual_elements(self, mentor):
        """Test that lessons include visual descriptions"""
        lesson = mentor.get_lesson(chapter=1, lesson=2)

        # Should reference chart elements
        content_lower = lesson["content"].lower()
        assert any(keyword in content_lower for keyword in [
            "chart", "candle", "pattern", "level", "structure"
        ])

    def test_call_to_action(self, mentor):
        """Test that lessons have actionable takeaways"""
        lesson = mentor.get_lesson(chapter=1, lesson=3)

        # Should have clear action items
        assert "key_points" in lesson
        assert len(lesson["key_points"]) > 0
