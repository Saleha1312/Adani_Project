from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ScrapedDataInput(BaseModel):
    url: str
    title: str
    headings: List[str]
    content: List[str]

class ScrapedData(ScrapedDataInput):
    id: str = Field(alias="_id", default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
