from app.ai.base import AIService


class MockAIService(AIService):
    def generate_feedback(self, matching_result: dict) -> dict:
        missing = matching_result.get("missing_skills", [])
        matched = matching_result.get("matched_skills", [])
        score = matching_result.get("matching_score", 0)
        compatibility = matching_result.get("compatibility", {})

        summary = self._create_summary(score)
        strengths = self._create_strengths(matched)
        weaknesses = self._create_weaknesses(missing)
        risk_flags = self._create_risk_flags(missing)
        recruiter_recs = self._create_recruiter_recommendations(score, missing)
        candidate_recs = self._create_candidate_recommendations(missing)
        questions = self._create_interview_questions(missing, matched)

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "risk_flags": risk_flags,
            "recommendations": {
                "for_recruiter": recruiter_recs,
                "for_candidate": candidate_recs,
            },
            "improvement_suggestions": candidate_recs,
            "interview_questions": questions,
        }

    def _create_summary(self, score: float) -> str:
        if score >= 85:
            return "CV có độ phù hợp rất cao với JD. Ứng viên đáp ứng tốt hầu hết yêu cầu tuyển dụng."
        if score >= 70:
            return "CV có độ phù hợp tốt với JD. Ứng viên có nhiều kỹ năng liên quan và nên được đưa vào vòng phỏng vấn."
        if score >= 55:
            return "CV có độ phù hợp trung bình. Ứng viên có nền tảng phù hợp nhưng cần bổ sung thêm một số kỹ năng hoặc bằng chứng dự án."
        if score >= 40:
            return "CV có độ phù hợp thấp. Ứng viên còn thiếu nhiều yêu cầu quan trọng so với JD."
        return "CV chưa phù hợp với JD hiện tại."

    def _create_strengths(self, matched_skills: list[str]) -> list[str]:
        if not matched_skills:
            return ["CV chưa thể hiện rõ các kỹ năng trùng với JD."]
        return [
            f"Có các kỹ năng phù hợp với JD: {', '.join(matched_skills)}.",
            "Có thể dùng kết quả matching để định hướng vòng phỏng vấn kỹ thuật.",
        ]

    def _create_weaknesses(self, missing_skills: list[str]) -> list[str]:
        if not missing_skills:
            return ["Chưa phát hiện thiếu hụt kỹ năng lớn so với JD."]
        return [
            f"Thiếu các kỹ năng quan trọng trong JD: {', '.join(missing_skills)}.",
            "CV nên bổ sung thêm ví dụ dự án thực tế để tăng độ tin cậy.",
        ]

    def _create_risk_flags(self, missing_skills: list[str]) -> list[str]:
        important_skills = {"aws", "docker", "kubernetes", "celery", "redis", "postgresql"}
        risks = []
        for skill in missing_skills:
            if skill.lower() in important_skills:
                risks.append(f"Thiếu kỹ năng quan trọng: {skill}.")
        if not risks:
            risks.append("Không phát hiện rủi ro lớn từ phần kỹ năng.")
        return risks

    def _create_recruiter_recommendations(self, score: float, missing_skills: list[str]) -> list[str]:
        recs = []
        if score >= 70:
            recs.append("Nên đưa ứng viên vào vòng phỏng vấn tiếp theo.")
        elif score >= 55:
            recs.append("Có thể cân nhắc phỏng vấn nếu nguồn ứng viên chưa nhiều.")
        else:
            recs.append("Không nên ưu tiên ứng viên này cho vị trí hiện tại.")
        if missing_skills:
            recs.append(f"Nên hỏi kỹ về các kỹ năng còn thiếu: {', '.join(missing_skills)}.")
        recs.append("Nên yêu cầu ứng viên mô tả dự án thực tế đã từng tham gia.")
        return recs

    def _create_candidate_recommendations(self, missing_skills: list[str]) -> list[str]:
        suggestions = [
            "Đưa các kỹ năng khớp với JD lên phần đầu CV.",
            "Bổ sung mô tả dự án thực tế, vai trò cụ thể và kết quả đạt được.",
            "Viết rõ công nghệ đã dùng, quy mô hệ thống và trách nhiệm cá nhân.",
        ]
        if missing_skills:
            suggestions.append(f"Bổ sung hoặc làm rõ kinh nghiệm liên quan đến: {', '.join(missing_skills)}.")
        return suggestions

    def _create_interview_questions(self, missing_skills: list[str], matched_skills: list[str]) -> list[str]:
        questions = []
        for skill in matched_skills[:3]:
            questions.append(f"Bạn hãy mô tả kinh nghiệm thực tế của bạn với {skill}?")
        for skill in missing_skills[:3]:
            questions.append(f"Bạn đã từng làm việc với {skill} chưa? Nếu có, hãy mô tả dự án cụ thể.")
        questions.append("Bạn hãy mô tả một dự án gần nhất và vai trò cụ thể của bạn trong dự án đó.")
        questions.append("Bạn đã từng xử lý lỗi hoặc tối ưu hiệu năng hệ thống backend như thế nào?")
        return questions
