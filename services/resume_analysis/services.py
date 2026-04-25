import os

import fitz

from .models import CV, JobDescription, MatchReport
from services.gemini import GeminiClient


class ResumeAnalysisService:
    def _extract_text(self, file_field):
        path = file_field.path
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            with fitz.open(path) as doc:
                return "\n".join(page.get_text() for page in doc)[:18000]
        with open(path, "rb") as handle:
            return handle.read().decode("utf-8", errors="ignore")[:18000]

    def compare(self, jd_id, cv_ids, user=None):
        jd = JobDescription.objects.get(id=jd_id, user=user) if user else JobDescription.objects.get(id=jd_id)
        jd_text = self._extract_text(jd.file)
        ai = GeminiClient()
        results = []

        for cv in CV.objects.filter(id__in=cv_ids, user=user):
            cv_text = self._extract_text(cv.file)
            prompt = (
                "Compare this resume/CV against the job description. Return concise sections: "
                "Match score from 0 to 100, strongest matches, gaps, and suggested resume edits.\n\n"
                f"JOB DESCRIPTION:\n{jd_text}\n\nCV:\n{cv_text}"
            )
            analysis = ai.generate_text([ai.text_content("user", prompt)])
            score = self._score_from_text(analysis)
            MatchReport.objects.create(jd=jd, cv=cv, score=score, details={"analysis": analysis})
            results.append({"cv_id": cv.id, "score": score, "details": {"analysis": analysis}})
        return results

    def _score_from_text(self, text):
        import re

        match = re.search(r"(\d{1,3})(?:\s*/\s*100|\s*%)", text)
        if not match:
            return 0.0
        return float(max(0, min(100, int(match.group(1)))))
