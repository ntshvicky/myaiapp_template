# stub: replace with real embedding + comparison
class ResumeAnalysisService:
    def compare(self, jd_id, cv_ids):
        # returns list of dicts with cv_id, score, details
        return [{"cv_id":cv, "score":0.5, "details":{"match":"stub"}} for cv in cv_ids]
