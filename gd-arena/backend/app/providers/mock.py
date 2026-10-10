from datetime import datetime, timezone

from app.models.schemas import FeedbackReport, ReportSection, TranscriptMessage
from app.providers.base import LLMProvider, SpeechToTextProvider, TextToSpeechProvider


PARTICIPANTS = [
    {
        "name": "Riya",
        "label": "The Dominator",
        "style": "confident, challenging, forward-moving, never rude",
    },
    {
        "name": "Arjun",
        "label": "The Data-Driven Analyst",
        "style": "structured, factual, comparative, logical",
    },
    {
        "name": "Meera",
        "label": "The Quiet Builder",
        "style": "balanced, reflective, builds on others, asks thoughtful questions",
    },
]


class MockLLMProvider(LLMProvider):
    def participant_turn(
        self,
        participant: dict[str, str],
        topic: str,
        transcript: list[TranscriptMessage],
        phase: str,
        language: str = "en-IN",
    ) -> str:
        if language == "hi-IN":
            return self._hindi_participant_turn(participant["name"], topic, phase)
        last_student = next((m.text for m in reversed(transcript) if m.source == "student"), "")
        last_any = transcript[-1].text if transcript else ""
        name = participant["name"]
        if phase == "closing_round":
            return self._closing_response(name, topic, transcript)
        if name == "Riya":
            anchor = last_student or last_any or topic
            return (
                f"I want to push this point further. On '{topic}', we should not stay vague: "
                f"the key test is whether the idea actually works for students and employers. "
                f"Building on '{_short_quote(anchor)}', what concrete trade-off are we willing to accept?"
            )
        if name == "Arjun":
            return (
                f"I would structure this in three parts: access, outcomes, and risk. For '{topic}', "
                f"the strongest argument needs examples and comparison, not only opinion. "
                f"If we compare short-term convenience with long-term impact, the group can reach a clearer position."
            )
        return (
            f"I agree there are trade-offs, and I want to connect the points made so far. "
            f"Maybe the balanced view is that '{topic}' depends on context, safeguards, and who benefits. "
            f"Can we include quieter stakeholders before concluding?"
        )

    def moderator_message(self, topic: str, phase: str, transcript: list[TranscriptMessage], language: str = "en-IN") -> str:
        if language == "hi-IN":
            return self._hindi_moderator_message(topic, phase)
        if phase == "opening":
            return (
                f"Welcome to GD Arena. Today's topic is: {topic}. "
                "Keep responses concise, build on each other, and try to reach a balanced conclusion."
            )
        if phase == "closing_round":
            return "We are entering the closing round. Please give one crisp final point or recommendation."
        if phase == "ended":
            return "Thank you. The discussion is now closed. I will prepare a transcript-grounded feedback report."
        return "Let's keep the discussion moving. Respond to the latest point and add a fresh angle."

    def feedback_report(self, session_id: str, topic: str, transcript: list[TranscriptMessage]) -> FeedbackReport:
        student_messages = [m for m in transcript if m.source == "student" and m.text.strip()]
        ai_messages = [m for m in transcript if m.source == "ai"]
        has_evidence = len(student_messages) >= 2
        word_count = sum(len(message.text.split()) for message in student_messages)
        joined_student_text = " ".join(message.text.lower() for message in student_messages)
        builds_on_others = any(phrase in joined_student_text for phrase in ("building on", "i agree", "i disagree", "arjun", "riya", "meera", "however", "but"))
        overall_score = 1
        overall_score += sum(len(student_messages) >= count for count in (2, 3, 4, 6))
        overall_score += sum(word_count >= count for count in (50, 120, 220))
        overall_score += int(builds_on_others)
        rating = "Weak" if overall_score <= 3 else "Average" if overall_score <= 5 else "Strong" if overall_score <= 8 else "Elite"
        first_quote = student_messages[0].text if student_messages else None
        second_quote = student_messages[1].text if len(student_messages) > 1 else first_quote

        def section(score: str, explanation: str, quote: str | None, suggestion: str) -> ReportSection:
            if not quote:
                return ReportSection(
                    score="Not enough evidence",
                    explanation="The transcript does not include enough student speech to assess this fairly.",
                    quote=None,
                    suggestion="Add at least two spoken or typed turns before generating final feedback.",
                )
            return ReportSection(score=score, explanation=explanation, quote=quote, suggestion=suggestion)

        sections = {
            "speaking_participation": section(
                "Good" if has_evidence else "Limited",
                f"You contributed {len(student_messages)} turn(s) while the AI panel contributed {len(ai_messages)} turn(s).",
                first_quote,
                "Aim for steady but concise participation across the discussion.",
            ),
            "initiation": section(
                "Developing",
                "You entered the discussion, but initiation is stronger when you frame the problem and take a clear stance early.",
                first_quote,
                "Open with a one-line position, then support it with one reason.",
            ),
            "quality_of_ideas": section(
                "Promising",
                "Your ideas are usable when they include a reason or example.",
                second_quote,
                "Add evidence, comparison, or a real-world example to make each point sharper.",
            ),
            "building_on_others": section(
                "Developing",
                "The transcript shows room to explicitly connect your point to earlier speakers.",
                second_quote,
                "Use phrases like 'building on Arjun's point' or 'I partly disagree because...'.",
            ),
            "listening": section(
                "Fair",
                "Listening is visible when you reference what others said before adding your own point.",
                first_quote,
                "Mention one prior speaker before making a new claim.",
            ),
            "handling_interruptions": section(
                "Not enough evidence" if not has_evidence else "Calm",
                "This mock session did not include aggressive interruptions, so the rating is conservative.",
                first_quote if has_evidence else None,
                "If interrupted, briefly acknowledge the speaker and finish your sentence calmly.",
            ),
            "communication_clarity": section(
                "Clear" if has_evidence else "Limited",
                "Your wording is understandable; the next step is more structure.",
                first_quote,
                "Try point, reason, example, conclusion for each turn.",
            ),
            "conclusion": section(
                "Developing",
                "A strong GD conclusion summarizes consensus and gives a recommendation.",
                second_quote,
                "End with 'overall, our group recommends...' and include one reason.",
            ),
        }
        summary = (
            f"For the topic '{topic}', the student contributed enough material for directional feedback."
            if has_evidence
            else f"For the topic '{topic}', there is not enough student transcript evidence for a full assessment."
        )
        return FeedbackReport(
            session_id=session_id,
            topic=topic,
            overall_summary=summary,
            overall_score=overall_score,
            rating=rating,
            sections=sections,
            top_3_strengths=[
                "Entered the discussion instead of staying silent.",
                "Kept language understandable.",
                "Showed willingness to engage with a structured GD format.",
            ],
            top_3_improvements=[
                "Use more transcript-linked examples and evidence.",
                "Explicitly build on or challenge another speaker.",
                "Give a crisp closing recommendation.",
            ],
            generated_at=datetime.now(timezone.utc),
        )

    def _closing_response(self, name: str, topic: str, transcript: list[TranscriptMessage]) -> str:
        if name == "Riya":
            return f"My closing view: on '{topic}', the group should choose a clear side and defend it with practical impact."
        if name == "Arjun":
            return f"My conclusion is that '{topic}' should be judged through evidence, feasibility, and measurable outcomes."
        return f"I would conclude that '{topic}' needs a balanced recommendation that includes benefits, risks, and fairness."

    @staticmethod
    def _hindi_participant_turn(name: str, topic: str, phase: str) -> str:
        if phase == "closing_round":
            return f"मेरा निष्कर्ष है कि '{topic}' पर निर्णय लेते समय लाभ, जोखिम और सभी लोगों पर असर को साथ में देखना चाहिए।"
        if name == "Riya":
            return f"'{topic}' पर हमें केवल सामान्य बात नहीं करनी चाहिए। मेरा सवाल है कि इसका व्यावहारिक लाभ किसे मिलेगा और हम किस जोखिम को स्वीकार करेंगे?"
        if name == "Arjun":
            return f"मैं इसे तीन पहलुओं में देखूंगा: पहुंच, परिणाम और जोखिम। '{topic}' पर तर्क को उदाहरण और प्रमाण के साथ रखना जरूरी है।"
        return f"मैं दोनों पक्षों को जोड़ना चाहूंगी। '{topic}' में संदर्भ, सुरक्षा उपाय और जिन लोगों को लाभ मिलता है, उन्हें ध्यान में रखकर संतुलित निष्कर्ष निकल सकता है।"

    @staticmethod
    def _hindi_moderator_message(topic: str, phase: str) -> str:
        if phase == "opening":
            return f"GD Arena में आपका स्वागत है। आज का विषय है: {topic}. अपनी बात संक्षेप में रखें, दूसरों के विचारों पर बनाएं और संतुलित निष्कर्ष तक पहुंचें।"
        if phase == "closing_round":
            return "अब अंतिम चरण है। कृपया एक स्पष्ट अंतिम बिंदु या सुझाव दें।"
        if phase == "ended":
            return "धन्यवाद। चर्चा समाप्त हो गई है। अब आपकी बातचीत के आधार पर रिपोर्ट तैयार की जाएगी।"
        return "चर्चा को आगे बढ़ाएं। पिछले बिंदु का जवाब दें और एक नया दृष्टिकोण जोड़ें।"


class MockSpeechToTextProvider(SpeechToTextProvider):
    def transcribe(self, audio_bytes: bytes) -> str:
        return ""


class MockTextToSpeechProvider(TextToSpeechProvider):
    def synthesize(self, text: str) -> bytes:
        return b""


def _short_quote(text: str, max_len: int = 70) -> str:
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
