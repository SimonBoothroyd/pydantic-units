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
It is lightweight and has no dependencies beyond Pydantic and OpenMM.

All units that are available in OpenMM are supported except for `'ampere'` whose symbol
conflicts with the angstrom unit symbol, making parsing ambiguous. Angstroms can be
specified as either `'A'`, or `'Å'`.

## Installation

This package can be installed using `conda` (or `mamba`, a faster version of `conda`):

```shell
mamba install -c conda-forge pydantic-units
```

## Getting Started

The `OpenMMQuantity` class can be used as a field in a Pydantic model to represent a
quantity with units. It will both handle parsing quantities with units from strings and
checking that parsed units are compatible with the expected units.

Quantities can either be passed into models (see below for how to define models) with
such a field directly:

```python
from openmm import unit
MyModel(temperature=300.0 * unit.kelvin)
```

or they can be passed in as strings, in which case the unit can be specified either
fully

```python
MyModel(temperature='300.0 kelvin')
```

or with the unit symbol

```python
MyModel(temperature='300.0 K')
```

The field also handles validation of the unit, so that the following will raise a
validation error:

```python
MyModel(temperature='300.0 A')
# raises: Value error, invalid units angstrom - expected angstrom kelvin
```

### Pydantic V1

Due to limitations of custom fields in Pydantic v1, v1 models must define a custom
JSON encoder if the model needs to be serialised to JSON:

```python
from pydantic import BaseModel
from openmm import unit

from pydantic_units import OpenMMQuantity, quantity_serializer

class Model(BaseModel):
    class Config:
        json_encoders = {unit.Quantity: quantity_serializer}

    a: OpenMMQuantity[unit.angstrom]
    b: OpenMMQuantity[unit.kelvin]

model = Model(a=1.0 * unit.nanometer, b='298.0 K')
model.json()
# '{"a": "10.0 A", "b": "298.0 K"}'
```

### Pydantic V2

Pydantic v2 supports custom fields with custom encoders, so the `OpenMMQuantity` field
can be used directly in the model without needing to define a custom JSON encoder:

```python
from pydantic import BaseModel
from openmm import unit

from pydantic_units import OpenMMQuantity

class Model(BaseModel):
    a: OpenMMQuantity[unit.angstrom]
    b: OpenMMQuantity[unit.kelvin]

model = Model(a=1.0 * unit.nanometer, b='298.0 K')
model.model_dump_json()
# '{"a": "10.0 A", "b": "298.0 K"}'
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
    b: OpenMMQuantity[unit.kelvin]

model = Model(a=1.0 * unit.nanometer, b='298.0 K')
model.json()
# '{"a": "10.0 A", "b": "298.0 K"}'
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

quantity_validator('1.0 angstrom', unit.angstrom)
# Quantity(value=1.0, unit=angstrom)
quantity_validator('1.0 A', unit.angstrom)
# Quantity(value=1.0, unit=angstrom)
quantity_validator('1.0 kJ/mol', unit.kilojoules_per_mole)
# Quantity(value=1.0, unit=kilojoule/mole)
```

The leading `*` can be either included or omitted, and whitespace is usually ignored,
such that the following are all equivalent:

```python
from pydantic_units import quantity_validator
from openmm import unit

quantity_validator('1.0 A', unit.angstrom)
quantity_validator('1.0A', unit.angstrom)
quantity_validator('1.0 * A', unit.angstrom)
quantity_validator('1.0*A', unit.angstrom)
```
