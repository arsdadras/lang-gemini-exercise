"""What a caller asks of the P4 interpreter specialist: ``InterpreterInput``."""

from pydantic import BaseModel, Field


class InterpreterInput(BaseModel):
    """Typed input for the P4 sandboxed code interpreter specialist."""

    task: str = Field(
        description="Self-contained coding, execution, or analysis task for the sandbox."
    )
