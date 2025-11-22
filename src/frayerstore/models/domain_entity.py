from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class DomainEntity:
    """Base class for all domain entities with database identity."""

    pk: int

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash((type(self), self.pk))
