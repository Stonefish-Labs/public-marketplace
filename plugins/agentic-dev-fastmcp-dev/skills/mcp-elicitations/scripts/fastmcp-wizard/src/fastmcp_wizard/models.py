from dataclasses import dataclass
from typing import Any, Callable, Type, Optional

@dataclass
class FormStep:
    """
    Encapsulates a single elicitation step within a Progressive Disclosure Form Wizard.
    """
    step_id: str
    message: str
    schema: Optional[Type[Any]]
    condition: Optional[Callable[[dict[str, Any]], bool]] = None
    is_required: bool = True
