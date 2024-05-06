from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field

THREATENING = "threatening"
NON_THREATENING = "non-threatening"
HATEFUL = "hateful"
NEUTRAL = "neutral"

content_types = {
    THREATENING,
    NON_THREATENING,
    HATEFUL,
    NEUTRAL,
}


class DataFilteringParams(BaseModel):
    day: Optional[int] = Field(None, description="day of the month")
    month: Optional[int] = Field(None, description="month in numerical form")
    year: Optional[int] = Field(None, description="year to use for data retrieval")
    content_type: str = Field(
        "",
        description="Content type to retrieve. e.g. threatening, hateful, neutral",
    )

    # NOTE: I can add more logic to disallow day > 31
    # or let's say 30 days in month 2 (Feb)
    # but for simplicities sake, let's just keep like this.

    # threatening = threat_level in db == medium/high
    # non-threatening = threat_level in db == low/None
    # hateful = hateful in db == medium/high
    # neutral = threat_level in db == low/None and hateful in db == low/None

    @classmethod
    def validate_content_type(cls, content_type):
        if content_type is not None and content_type not in content_types:
            raise HTTPException(status_code=422, detail="Invalid content_type")
        return content_type

    @property
    def content_type_validated(self):
        return self.validate_content_type(self.content_type)
