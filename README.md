<h1 align="center">Pydantic Units</h1>

<p align="center">Support for OpenMM units as pydantic fields</p>

<p align="center">
  <a href="https://github.com/SimonBoothroyd/pydantic-units/actions?query=workflow%3Aci">
    <img alt="ci" src="https://github.com/SimonBoothroyd/pydantic-units/actions/workflows/ci.yaml/badge.svg?branch=main" />
  </a>
  <a href="https://codecov.io/gh/SimonBoothroyd/pydantic-units/branch/main">
    <img alt="coverage" src="https://codecov.io/gh/SimonBoothroyd/pydantic-units/graph/badge.svg?token=YNbFZ5L1VR" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img alt="license" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

---

The `pydantic-units` framework aims to offer a convenient way to work with OpenMM units
in Pydantic models, in a way that is backwards compatible with both Pydantic v1 and v2.

It is lightweight and has no dependencies beyond Pydantic and OpenMM. All units that
are available in OpenMM are supported except for `'ampere'` whose symbol is `'A'`,
which conflicts with the angstrom unit symbol.

## Installation

This package can be installed using `conda` (or `mamba`, a faster version of `conda`):

```shell
mamba install -c conda-forge pydantic-units
```

## Getting Started

The `OpenMMQuantity` class can be used as a field in a Pydantic model to represent a
quantity with units. It will both handle parsing quantities with units from strings and
checking that parsed units are compatible with the expected units.

### Pydantic V1

Due to limitations of custom fields in Pydantic v1, v1 models must define a custom
JSON encoder if the model needs to be serialised to JSON:

```python
from pydantic import BaseModel
from openmm.unit import Quantity, angstrom, nanometer

from pydantic_units import OpenMMQuantity, quantity_serializer

class Model(BaseModel):
    class Config:
        json_encoders = {Quantity: quantity_serializer}

    a: OpenMMQuantity[angstrom]
    b: OpenMMQuantity[nanometer]

model = Model(a='1.0 angstrom', b='1.0 nm')
model.json()
# '{"a": "1 A", "b": "1.0 nm"}'
```

### Pydantic V2

Pydantic v2 supports custom fields with custom encoders, so the `OpenMMQuantity` field
can be used directly in the model:

```python
from pydantic import BaseModel
from openmm import unit

from pydantic_units import OpenMMQuantity

class Model(BaseModel):
    a: OpenMMQuantity[unit.angstrom]
    b: OpenMMQuantity[unit.nanometer]

model = Model(a='1.0 angstrom', b='1.0 nm')
# OR
model = Model(a=1.0 * unit.angstrom, b=1.0 * unit.nanometer)

model.model_dump_json()
# '{"a": "1 A", "b": "1.0 nm"}'
```

Backwards compatibility with Pydantic v1 is also maintained:

```python
from pydantic.v1 import BaseModel
from openmm import unit

from pydantic_units import quantity_serializer
from pydantic_units.v1 import OpenMMQuantity

class Model(BaseModel):
    class Config:
        json_encoders = {unit.Quantity: quantity_serializer}

    a: OpenMMQuantity[unit.angstrom]
    b: OpenMMQuantity[unit.nanometer]

model = Model(a='1.0 angstrom', b='1.0 nm')
model.json()
# '{"a": "1 A", "b": "1.0 nm"}'
```

### (De)Serialization

Quantity fields will be serialized into JSON as strings with the unit symbol, e.g.

```python
from pydantic_units import quantity_serializer
from openmm import unit

print(quantity_serializer(1.0 * unit.angstrom))
# '1 A'
print(quantity_serializer(1.0 * unit.kilojoules_per_mole))
# '1.0 kJ * mol**-1'
```

Likewise, when instantiating a field from a string (either through the constructor or
through parsing JSON), the unit should be specified in the string as either the full
unit name or the unit symbol:

```python
from pydantic_units import quantity_validator
from openmm import unit

print(quantity_validator('1.0 angstrom', unit.angstrom))
# 1.0 A
print(quantity_validator('1.0 A', unit.angstrom))
# 1.0 A
print(quantity_validator('1.0 kJ/mol', unit.kilojoules_per_mole))
# 1.0 kJ/mol
```

The leading `*` can be either included or omitted, and whitespace is usually ignored:

```python
from pydantic_units import quantity_validator
from openmm import unit

print(quantity_validator('1.0 A', unit.angstrom))
# 1.0 A
print(quantity_validator('1.0A', unit.angstrom))
# 1.0 A
print(quantity_validator('1.0 * A', unit.angstrom))
# 1.0 A
print(quantity_validator('1.0*A', unit.angstrom))
# 1.0 A
```
