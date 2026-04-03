from pydantic import BaseModel
from typing import Optional, List

# --- Confidence-wrapped field ---
class ConfidenceField(BaseModel):
    value: Optional[str] = None
    confidence: float  # 0.0 to 1.0

# --- Candidate Details ---
class CandidateDetails(BaseModel):
    name: ConfidenceField
    father_name: ConfidenceField
    mother_name: ConfidenceField
    roll_no: ConfidenceField
    registration_no: ConfidenceField
    dob: ConfidenceField
    exam_year: ConfidenceField
    board_or_university: ConfidenceField
    institution: ConfidenceField

# --- Subject-wise Marks ---
class SubjectMarks(BaseModel):
    subject: ConfidenceField
    max_marks: ConfidenceField
    obtained_marks: ConfidenceField
    grade: ConfidenceField

# --- Overall Result ---
class OverallResult(BaseModel):
    result: ConfidenceField
    total_marks: ConfidenceField
    percentage: ConfidenceField
    division: ConfidenceField
    grade: ConfidenceField

# --- Issue Info ---
class IssueInfo(BaseModel):
    issue_date: ConfidenceField
    issue_place: ConfidenceField

# --- Full Extraction Response ---
class ExtractionResponse(BaseModel):
    candidate_details: CandidateDetails
    subjects: List[SubjectMarks]
    overall_result: OverallResult
    issue_info: IssueInfo

# --- JWT Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    username: str
    password: str