Mutators
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Mutators are the drivers of minimizations. Given a node, they apply modifications to produce new (simpler) nodes that can replace the original one.
A mutator class should at least look like this:

.. code-block:: python3

    class Dummy:
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

Below follows a list of all available mutators, grouped by their main concern: generic mutators that work on the node structure, SMT-LIB mutators that deal with certain SMT-LIB constructs, and mutators for individual SMT-LIB theories.

Most mutators can be enabled or disabled using options of the form :code:`--<mutator>` or :code:`--no-<mutator>` (like :code:`--no-constants`), most are enabled by default. The same is possible for all mutators from a group with :code:`--<group>` or :code:`--no-<group>` (like :code:`--no-generic`).
:doc:`Preconfigured modes <modes>` for common tasks are available as well.

Generic mutators
----------------

.. autoclass:: pydelta.mutators_core.Constants
.. autoclass:: pydelta.mutators_core.EraseChildren
.. autoclass:: pydelta.mutators_core.MergeWithChildren
.. autoclass:: pydelta.mutators_core.ReplaceByVariable
.. autoclass:: pydelta.mutators_core.SortChildren
.. autoclass:: pydelta.mutators_core.SubstituteChildren
.. autoclass:: pydelta.mutators_core.TopLevelBinaryReduction

Arithmetic mutators
-------------------
.. autoclass:: pydelta.mutators_arithmetic.ArithmeticSimplifyConstant
.. autoclass:: pydelta.mutators_arithmetic.ArithmeticNegateRelations
.. autoclass:: pydelta.mutators_arithmetic.ArithmeticSplitNaryRelations
.. autoclass:: pydelta.mutators_arithmetic.ArithmeticStrengthenRelations

Bitvector mutators
------------------
.. autoclass:: pydelta.mutators_bitvectors.BVConcatToZeroExtend
.. autoclass:: pydelta.mutators_bitvectors.BVExtractConstants
.. autoclass:: pydelta.mutators_bitvectors.BVOneZeroITE
.. autoclass:: pydelta.mutators_bitvectors.BVSimplifyConstant

Boolean mutators
----------------
.. autoclass:: pydelta.mutators_boolean.DeMorgan
.. autoclass:: pydelta.mutators_boolean.DoubleNegation
.. autoclass:: pydelta.mutators_boolean.EliminateFalseEquality
.. autoclass:: pydelta.mutators_boolean.EliminateImplications
.. autoclass:: pydelta.mutators_boolean.NegatedQuantifiers
.. autoclass:: pydelta.mutators_boolean.XORRemoveConstants
.. autoclass:: pydelta.mutators_boolean.XOREliminateBinary

SMT-LIB mutators
----------------
.. autoclass:: pydelta.mutators_smtlib.CheckSatAssuming
.. autoclass:: pydelta.mutators_smtlib.EliminateDistinct
.. autoclass:: pydelta.mutators_smtlib.InlineDefinedFuns
.. autoclass:: pydelta.mutators_smtlib.LetElimination
.. autoclass:: pydelta.mutators_smtlib.LetSubstitution
.. autoclass:: pydelta.mutators_smtlib.PushPopRemoval
.. autoclass:: pydelta.mutators_smtlib.SimplifyLogic
.. autoclass:: pydelta.mutators_smtlib.SimplifyQuotedSymbol
.. autoclass:: pydelta.mutators_smtlib.VariableNames

String mutators
---------------
.. autoclass:: pydelta.mutators_strings.StringSimplifyConstant
