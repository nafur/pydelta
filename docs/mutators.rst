Mutators
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Mutators are the drivers of minimizations. Given a node, they apply modifications to produce new (simpler) nodes that can replace the original one.
A mutator class should at least look like this:

.. code-block:: python3

    class PassDummy:
        def filter(self, node):
            """Check whether this mutators can be applied to the given node.
            If not specified, we use `True`"""
            return True
        def mutations(self, node):
            """Create a list of mutations of the given node."""
            return []
        def __str__(self):
            """Returns a description of this mutator."""
            return "dummy"

Generic mutators
----------------

.. autoclass:: mutators_generic.PassConstant
.. autoclass:: mutators_core.PassEraseChildren
.. autoclass:: mutators_core.PassSubstituteChildren
.. autoclass:: mutators_core.PassSortChildren
.. autoclass:: mutators_core.PassMergeWithChildren
.. autoclass:: mutators_core.PassReplaceVariables
.. autoclass:: mutators_core.PassLetSubstitution
.. autoclass:: mutators_core.PassLetElimination
.. autoclass:: mutators_core.PassInlineDefinedFuns

Boolean mutators
----------------
.. autoclass:: mutators_boolean.PassBoolConstant

Arithmetic mutators
-------------------
.. autoclass:: mutators_arithmetic.PassArithmeticConstant

Bitvector mutators
------------------
.. autoclass:: mutators_bitvectors.PassBVConstant
.. autoclass:: mutators_bitvectors.PassBVExtractConstants
