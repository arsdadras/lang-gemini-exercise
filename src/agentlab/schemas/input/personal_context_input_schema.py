"""What a caller asks of the P5 personal-context specialist: ``PersonalContextInput``."""

from pydantic import BaseModel, Field


class PersonalContextInput(BaseModel):
    """Typed input for the P5 personal-context specialist."""

    user_id: str = Field(
        description="Identifier of the user whose long-term memory and skills to load."
    )
