API Documentation
=================
Most classes below are generic over :py:class:`~class_registry.base.ValueType`
(the registered class) and :py:class:`~class_registry.base.KeyType` (the public
registry key, defaulting to :py:class:`str`).  See
:py:class:`~class_registry.base.BaseRegistry` for what each type parameter
means.  :py:class:`~class_registry.entry_points.EntryPointClassRegistry` is
the exception: its keys are entry point names, so it pins ``KeyType`` to
:py:class:`str`.

.. The special methods below are listed by hand, one for each the prose
   cross-references: the template-owned conf.py's ``"special-members": False``
   default replaces any ``:special-members:`` option given here, so that option
   has no effect.  ``D`` is not in ``class_registry.base.__all__``, so
   automodule skips it; it follows the module so the public API comes first.

.. automodule:: class_registry.base
   :exclude-members: BaseRegistry

   .. autoclass:: BaseRegistry

      .. automethod:: __dir__
      .. automethod:: __getitem__
      .. automethod:: __len__

.. autoclass:: class_registry.base.D

.. automodule:: class_registry.cache
   :exclude-members: ClassRegistryInstanceCache

   .. autoclass:: ClassRegistryInstanceCache

      .. automethod:: __getitem__

.. automodule:: class_registry.entry_points
.. automodule:: class_registry.patcher
.. automodule:: class_registry.registry
