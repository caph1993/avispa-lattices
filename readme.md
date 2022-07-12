# Avispa lattices

`pip3 install avispa-lattices`

Avispa-lattices is a python package for working with finite partially ordered sets (posets), specially with lattices and join-endomorphisms, i.e. monotonic functions from a lattice to itself that preserve least upper bounds.
It is developed by the AVISPA team 2020-today.

Functionalities:

 - Display a poset or a lattice, possibly in a jupyter notebook and with functions on it.
 - Test if a poset is a lattice or if a lattice is distributive or modular, and explain precisely why not if not.
 - Test if two posets are equivalent and find the permutation of the elements that makes them equal.
 - Hash a poset or lattice in such a way that two equivalent* posets hash always to the same value. *if there is a permutation of the elements making them exactly equal.
 - Create a poset or lattice based on an adjoint matrix or an adjoint list.
 - Create a random poset or lattice of given size.
 - Iterate over all join-endomorphisms of a lattice.
 - Iterate over all lattices from size zero up to 12.
 - Compute the greatest lower bound of two join-endomorphisms.
 - Compute the poset of join-irreducible elements of a distributive lattice.
 - Compute the distributive lattice of down-sets of a poset.
 - Iterate over all elements of a lattice in toposort order.

All methods and properties that are either hard to compute or frequently used are cached to speed up further computations on the same lattice.

All methods are typed and or documented.

<!-- # Examples

```py
L = AL.random_lattice(12, seed=42)
L.show()
``` -->

## Contributors

 - Carlos Pinzón
 - Santiago Quintero, and his library https://github.com/Sirquini/delta
 - Sergio Ramírez
 - Frank Valencia
 - Code from https://www.sagemath.org/index.html

