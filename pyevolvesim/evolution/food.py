"""Food class for the evolution simulation."""

from pydantic import BaseModel, Field


class Food(BaseModel):
    """Food that creatures can consume for energy."""

    x: int
    y: int
    energy: float = Field(ge=0)
