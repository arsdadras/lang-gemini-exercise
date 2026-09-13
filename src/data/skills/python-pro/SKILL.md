---
name: python-pro
description: Professional Python engineering standards, modern type hints, and clean architectural idioms.
---

# Python Pro Skill

Follow these engineering guidelines whenever writing or refactoring Python code:

1. **Modern Type Hints:**
   - Always use built-in collection types for hints (`list[str]`, `dict[str, Any]`, `tuple[int, ...]`) instead of `typing.List` or `typing.Dict`.
   - Use union operator `A | B` instead of `typing.Union[A, B]` or `typing.Optional[A]`.

2. **Explicit Function Signatures:**
   - Provide complete type annotations for all public parameters and return types.

3. **No Legacy Hacks:**
   - Use `pathlib.Path` methods (e.g. `is_relative_to()`) rather than string manipulation.
   - Avoid mutable default arguments.

4. **Single Responsibility:**
   - Keep node functions and utilities modular, concise, and focused on a single task.
