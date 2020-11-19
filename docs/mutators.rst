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
        def global_mutations(self, linput, ginput):
            """Create a list of mutations of the whole input."""
            return []
        def __str__(self):
            """Returns a description of this mutator."""
            return "dummy"

Note that a mutator can work in two ways: :code:`mutations` constructs **local** replacements for a given node. :code:`global_mutations` on the other hand constructs **global** replacements for the whole input, given both a specific node and the current input. The idea for the latter is that some node (:code:`linput`) triggers a simplification that needs to be applied to the whole input (:code:`ginput`) at once, for example variable renaming or simplification of constants that occur multiple times.

Generic mutators
----------------

.. autoclass:: pydelta.mutators_core.PassConstants
.. autoclass:: pydelta.mutators_core.PassEliminateDistinct
.. autoclass:: pydelta.mutators_core.PassEraseChildren
.. autoclass:: pydelta.mutators_core.PassInlineDefinedFuns
.. autoclass:: pydelta.mutators_core.PassLetElimination
.. autoclass:: pydelta.mutators_core.PassLetSubstitution
.. autoclass:: pydelta.mutators_core.PassMergeWithChildren
.. autoclass:: pydelta.mutators_core.PassReplaceByVariable
.. autoclass:: pydelta.mutators_core.PassSortChildren
.. autoclass:: pydelta.mutators_core.PassSubstituteChildren
.. autoclass:: pydelta.mutators_core.PassVariableNames

Arithmetic mutators
-------------------
.. autoclass:: pydelta.mutators_arithmetic.PassArithmeticSimplifyConstant
.. autoclass:: pydelta.mutators_arithmetic.PassArithmeticNegateRelations
.. autoclass:: pydelta.mutators_arithmetic.PassArithmeticSplitNaryRelations
.. autoclass:: pydelta.mutators_arithmetic.PassArithmeticStrengthenRelations

Bitvector mutators
------------------
.. autoclass:: pydelta.mutators_bitvectors.PassBVConcatToZeroExtend
.. autoclass:: pydelta.mutators_bitvectors.PassBVExtractConstants
.. autoclass:: pydelta.mutators_bitvectors.PassBVOneZeroITE
.. autoclass:: pydelta.mutators_bitvectors.PassBVSimplifyConstant

Boolean mutators
----------------
.. autoclass:: pydelta.mutators_boolean.PassDeMorgan
.. autoclass:: pydelta.mutators_boolean.PassDoubleNegation
.. autoclass:: pydelta.mutators_boolean.PassEliminateFalseEquality
.. autoclass:: pydelta.mutators_boolean.PassEliminateImplications
.. autoclass:: pydelta.mutators_boolean.PassNegatedQuantifiers

SMT-LIB mutators
----------------
.. autoclass:: pydelta.mutators_smtlib.PassCheckSatAssuming
.. autoclass:: pydelta.mutators_smtlib.PassPushPopRemoval
.. autoclass:: pydelta.mutators_smtlib.PassSimplifyLogic

String mutators
---------------
.. autoclass:: pydelta.mutators_strings.PassStringSimplifyConstant
