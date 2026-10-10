from app.models.schemas import Phase, TranscriptMessage


class ModeratorStateMachine:
    closing_after_student_turns = 3

    def next_after_student_turn(self, current_phase: Phase, transcript: list[TranscriptMessage]) -> Phase:
        if current_phase == "opening":
            return "active_discussion"
        if current_phase == "active_discussion":
            student_turns = len([m for m in transcript if m.source == "student"])
            return "closing_round" if student_turns >= self.closing_after_student_turns else "active_discussion"
        return current_phase

    def next_after_ai_turn(self, current_phase: Phase, transcript: list[TranscriptMessage]) -> Phase:
        if current_phase == "closing_round":
            closing_ai_turns = len(
                [
                    m
                    for m in transcript
                    if m.source == "ai" and ("closing" in m.text.lower() or "conclude" in m.text.lower())
                ]
            )
            if closing_ai_turns >= 3:
                return "ended"
        return current_phase
