Modes of operation
====================================

By default, pyDelta enables (almost) all mutators and allows to disable (and enable) all mutators individually.
Alternatively, pyDelta provides several modes:

Aggressive
----------

With ``--mode-aggressive`` only mutations are checked that remove a minimum percentage of the input (measured in the number of nodes).
This percentage can be specified with ``--aggressiveness``.

Let elimination
---------------
With ``--mode-let-elimination`` only mutators that remove let binders are enabled, namely :class:`pydelta.mutators_core.PassLetElimination` and :class:`pydelta.mutators_core.PassLetSubstitution`.
If sometimes is useful to combine this mode with ``--run-unchecked`` to skip checking entirely and quickly eliminate all let binders.

Reduction only
--------------
With ``--mode-reduction-only`` only mutations are checked that reduce the size of the input (measured in the number of nodes).