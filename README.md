# Endgame Models

[Basic simulation example](./examples/test_generic_sim.py)

[Endgame simulation example](./examples/test_endgame_sim.py)

# FAQs

# Why make endgame simulations?

Lots of disease simulations possess similarities in their design, but not always in the specifics of their
implementation. The aim of endgame simulations is to provide a structure from which other disease models can
be implemented, regimenting their structure, and allowing for a consistent interface.

# Why use typing, generics and protocols?

Advanced use of typing through generics and protocols may be unfamiliar to some users, so I'll provide
here an explanation of why these are useful in this context. Types in general are useful for reducing
frequency of bugs in code, by use of a "type checker". A type checker confirms that functions/classes are
consistent in their expections of what a class looks like (methods it exposes etc). It prevents issues like
returning the wrong object by accident, or even more subtle mistakes like using a collection of the object
in one place vs the object in another. 

Endgame simulations is a library that represents a framework for how to create a simulation of a particular
structure, and for this purpose generic types are very useful. Models differ in their internal parameters, so suppose I want to say I expect a class like this:

```py
class Endgame:
    params: X
```

But what is X here? We can't know it's structure, so we use generics to say the type is insertable:

```py

Params = TypeVar("Params")

class Endgame(Generic[Params]):
    params: Params
```

# Why use pydantic for parameters?

## Structure

Frequently in disease simulations, there are many parameters used to control aspects of the simulation.
The first motivation for using a data validation library like Pydantic for this purpose, is to provide
the parameters with a typed structure. Now we know where parameters are defined, and we can track through the
code when parameters are used. Also, a type checker will flag if there are inconsistenties.

Note: It should be noted that a simpler structure like a "dataclass" would also fulfil this purpose, but there
are other reasons below for why pydantic models specifically are useful.

## Json validation

We wish to provide a generic json structure to represent the simulation controls. Pydantic provides a way to
validate this structure and make sure it's of the correct form, prior to any simulation being run, and parse 
it into our structured object form. This prevents a missing parameter only being found some way into the 
simulation running.

## Generic models

Unlike dataclasses, Pydantic models support the use of generic model structures for validation. As already established,
we need generics for the endgame model, so again, pydantic makes sense.
