# FastMCP 3 Elicitation UI Controls & SEP-1330 Typing

FastMCP 3 simplifies the generation of complex UI schemas via Python type hints. By strictly adhering to Specification Enhancement Proposal 1330 (SEP-1330), it maps common Python collections to robust frontend components.

## Type Mapping Reference

The following table dictates how you MUST annotate the `schema` (in `FormStep`) or `response_type` (in `ctx.elicit()`) to generate specific interfaces:

| Python Type Definition | FastMCP 3 UI Abstraction | Client Interface Rendering | Resulting Data Payload on Accept |
| :--- | :--- | :--- | :--- |
| `str`, `int`, `bool`, `float` | Scalar Object Wrapper | Single text input, numeric spinner, or boolean toggle switch. | Unwrapped scalar value (e.g., `"user_name"`, `42`, `True`). |
| `["low", "medium", "high"]` | Single-Select (Untitled) | Standard dropdown menu enforcing constrained choice. | The exact string selected by the user. |
| `{"low": {"title": "Low Priority"}}` | Single-Select (Titled) | Dropdown menu displaying human-readable titles while mapping to backend values. | The raw key associated with the selected title. |
| `[["bug", "feature", "docs"]]` | Multi-Select (Untitled) | A checklist or multi-select tag input allowing multiple concurrent selections. | A Python list containing the selected strings. |
| `[{"low": {"title": "Low Priority"}}]` | Multi-Select (Titled) | A titled checklist enabling multiple selections with human-readable labels. | A Python list containing the selected raw keys. |
| `dataclass` or `BaseModel` | Complex Structured Form | A composite form containing multiple distinct input fields tailored to the object properties. | An instantiated Python object populated with the user's data. |
| `None` | Pure Action Elicitation | A simple confirmation modal presenting only Accept, Decline, and Cancel buttons. | None (Used exclusively to capture explicit user consent). |

## Critical Implementation Details

### 1. Multi-Select Array Dimensions
It is a common error to use `["read", "write"]` for a multi-select. That generates a **single-select dropdown**. To generate a multi-select checklist, you MUST wrap the list in an additional array dimension: `[["read", "write"]]`.

### 2. Titled Mapping Dictionaries
When you need the UI to display a human-readable title (e.g., "Production Environment") but return a rigid backend key (e.g., `"prod"`), you must use the nested dictionary syntax:
```python
schema = {"prod": {"title": "Production Environment"}, "dev": {"title": "Development Workspace"}}
```
For a multi-select version of this, wrap it in a list:
```python
schema = [{"prod": {"title": "Production Environment"}, "dev": {"title": "Development Workspace"}}]
```

### 3. Pure Action Elicitation
If you only need the user's explicit consent to proceed (e.g., "Are you sure you want to delete this database?"), set the schema to `None`. The client will render an explicit confirmation modal without any input fields. You then pattern match on `AcceptedElicitation` or `CancelledElicitation`.