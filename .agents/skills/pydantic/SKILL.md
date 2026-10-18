---
name: pydantic
description: Pydantic data validation and serialization best practices. Use when defining models, adding constraints, validators, discriminated unions, or working with Pydantic type coercion and serialization.
---

# Pydantic Validation

In a nutshell, Pydantic is dataclasses with runtime validation. It leverages type
hints to understand how validation (and serialization) should be performed. It is
mostly useful when dealing with external untrusted data, for example when defining
an HTTP API.

It is generally *not* recommended to use Pydantic to define classes that are
instantiated within the user code. By doing so, you lose flexibility (e.g. you
cannot use types not supported by Pydantic, and it is harder to perform post-init
changes). It is usually better to use vanilla classes (or standard library
dataclasses) in this case, as a static type checker will already catch type
mismatches.

## Basic usage

```python
from datetime import date

from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str
    age: int = Field(description='The age of the person')
    birthdate: date | None = None


p = Person(name='John', age=20, birthdate='1970-01-01')
```

Pydantic coerces compatible input: the ISO date string `'1970-01-01'` is parsed
into a `date`.

## Constraints and field metadata

The `Field()` function is used to provide metadata and constraints. Distinguish
two types of metadata:

- *field specific* metadata: `deprecated`, `alias`, etc. that only have meaning
  attached to a field.
- *type specific* metadata: constraints such as `gt`, `max_length`, and metadata
  affecting JSON Schema (`description`, `title`).

Model fields are declared with `Field()` using the assignment form:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    first_name: str = Field(alias='name')
```

or using the annotated pattern:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    value: Annotated[int, Field(deprecated=True)] = 1
```

The annotated pattern has advantages:

- The `f: <type> = Field()` form (no default) can be confusing — it tricks users
  into thinking `f` has a default value, while the field is still required.
- You can provide an arbitrary amount of metadata elements for a field.

But note:

- Use the assignment form for metadata meaningful to static type checkers:
  `alias`, `default`, `default_factory`.
- *field specific* metadata can only be used on the "top-level" type. A common
  pitfall:

  ```python
  from typing import Annotated
  from pydantic import BaseModel, Field


  class Model(BaseModel):
      field_bad: Annotated[int, Field(deprecated=True)] | None = None
      field_ok: Annotated[int | None, Field(deprecated=True)] = None
  ```

  *field specific* metadata should apply to the whole union in this example.

### Constraints

As much as possible, use the "built-in" validation constraints instead of custom
validators:

```python
from typing import Annotated

from annotated_types import Gt
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    constrained_int_ok: Annotated[int, Gt(1)]  # good

    constrained_int_bad: int

    @field_validator('constrained_int_bad')  # bad
    @classmethod
    def validate(cls, v: int) -> int:
        if not v > 1:
            raise ValueError('Value is not greater than 1')
        return v
```

Sometimes constraints can't be expressed using `Field()`. String constraints such
as `strip_whitespace`, `to_upper`, `to_lower`, `ascii_only` can only be specified
using `pydantic.StringConstraints`:

```python
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class Model(BaseModel):
    # Do this instead of a validator calling s.strip():
    a: Annotated[str, StringConstraints(strip_whitespace=True)]
```

### Validators

In some cases you may have to use custom validators. As much as possible, use
*after* validators — they run after Pydantic validation, so the value is already
the field's type. *Before* validators receive input that can be anything, which is
error-prone.

Prefer the annotated pattern:

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel, field_validator


def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} is not an even number')
    return value


class Model(BaseModel):
    # Prefer this form: the validator is right next to the field.
    even: Annotated[int, AfterValidator(is_even)]
    odd: int

    # If you use the decorator form, define it as a classmethod.
    @field_validator('odd', mode='after')
    @classmethod
    def is_odd(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError(f'{value} is not an odd number')
        return value
```

### Type coercion, collections and unions

Unless you use strict mode, Pydantic applies type coercion in most cases. A field
typed `int` accepts strings like `'123'`. Collection types coerce too:
`list[str]` accepts tuples, sets, etc.

Avoid:

- unions such as `int | str` if your goal is to coerce the `str` to an `int`.
- abstract collections such as `collections.abc.Sequence` to accept both lists and
  tuples — inefficient.

Unions are best avoided in general: every use of the field needs to check each
type before doing anything with it.

#### Forward annotations

Python can write annotations as forward references (strings), which is hard for
Pydantic to evaluate. Avoid `from __future__ import annotations` in model modules
if possible. Only add explicit quotes to annotations not yet defined:

```python
from pydantic import BaseModel


class Model(BaseModel):
    self_ref: 'Model'
```

In Python >= 3.14, annotation evaluation is deferred, so you should not use string
annotations at all.

#### Recursive type aliases

Don't define recursive aliases as quoted `TypeAlias`:

```python
from typing import TypeAlias

# Pydantic generally can't evaluate this:
JsonValue: TypeAlias = 'list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None'
```

Use an explicit type alias (`type` on Python 3.12+, or `TypeAliasType`):

```python
type JsonValue = list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None

# Or, if not on Python >= 3.12:
from typing_extensions import TypeAliasType

JsonValue = TypeAliasType(
    'JsonValue',
    'list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None',
)
```

### Model subclasses, discriminated unions

Subclassing is common but a footgun in Pydantic:

```python
from pydantic import BaseModel


class Base(BaseModel):
    base_field: int


class Sub1(Base):
    sub1_field: str


class Main(BaseModel):
    model: Base


m = Main(model=Sub1(base_field=1, sub1_field='test'))
m.model_dump()
# {'model': {'base_field': 1}}  -> sub1_field missing!
```

Pydantic serializes according to the *declared* type (`Base`), not the runtime
subclass. Validation follows the same rule.

Instead, use discriminated unions (if you can set a discriminator field):

```python
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field


class Sub1(Base):
    type: Literal['sub1']
    sub1_field: str


class Sub2(Base):
    type: Literal['sub2']
    sub2_field: bool


Subs: TypeAlias = Annotated[Sub1 | Sub2, Field(discriminator='type')]


class Main(BaseModel):
    model: Subs
```

or generics:

```python
from pydantic import BaseModel


class Main[BaseT: Base](BaseModel):
    model: BaseT
```

If neither fits, use polymorphic serialization (Pydantic >=2.13) or
*serialize as any* (Pydantic <2.13) as a last resort.
