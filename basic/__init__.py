from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json


class Formats(str, Enum):
    SIMPLE_STRING = "simple_string"


@dataclass_json
@dataclass
class TraitAttribute:
    """Attribute of a trait"""
    name: str
    description: str
    format: Formats

    def validate(self, instance: (str, str)):
        assert instance[0] == self.name
        # We only have simple strings for now so always true
        # FIXME validate format


@dataclass_json
@dataclass
class DataTraitInstance:
    """The instance of a Data Trait

    Each attribute of the DataTrait must be defined
    """
    trait_instances: dict[str, str]
    title: str


@dataclass_json
@dataclass
class DataTrait:
    """Symbolizes a class of data

    Each class of data has a title and consists of a set of attributes that must be defined for each Instance of this.
    """
    title: str
    description: str
    fields: list[TraitAttribute]
    version: int

    def validate(self, trait: DataTraitInstance):
        attr_definition = {}
        for field in self.fields:
            attr_definition[field.name] = field
        attr_values = trait.trait_instances

        # calculate which keys are missing
        missing_keys = [x for x in attr_definition.keys() if x not in attr_values]
        wrong_keys = [x for x in attr_values.keys() if x not in attr_definition]

        if len(wrong_keys) != 0 or len(missing_keys) != 0:
            raise KeyError(f"Missing {wrong_keys} {missing_keys}")

        # now verify the attribute
        for available_key in attr_values.keys():
            attr_definition[available_key].validate((available_key, attr_values[available_key]))
