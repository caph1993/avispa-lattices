from . import validation as validation
from . import graph as graphs
from . import graphviz as graphviz
from . import description as description
from . import identity as identity
from . import interface as interface

# class IdentityMethods:

#     # hash = hash_methods.hash
#     # hash_elems = hash_methods.hash_elems
#     _hash = hash_methods._hash
#     _hash_elems = hash_methods._hash_elems
#     find_isomorphism = hash_methods.find_isomorphism
#     canonical = hash_methods.canonical
#     reindex = hash_methods.reindex

# class TaxonomyMethods:

#     # assert_poset = taxonomy_methods.assert_poset
#     # is_poset = taxonomy_methods.is_poset
#     # assert_lattice = taxonomy_methods.assert_lattice
#     # is_lattice = taxonomy_methods.is_lattice
#     # is_distributive = taxonomy_methods.is_distributive
#     # explain_non_distributive = taxonomy_methods.explain_non_distributive
#     # assert_distributive = taxonomy_methods.assert_distributive
#     # is_modular = taxonomy_methods.is_modular
#     # explain_non_modular = taxonomy_methods.explain_non_modular
#     # assert_modular = taxonomy_methods.assert_modular
#     pass

# class GraphMethods:

#     # bottom = graph_methods.bottom
#     # top = graph_methods.top
#     # heights = graph_methods.heights
#     # height = graph_methods.height
#     subgraph = graph_methods.subgraph
#     toposort = graph_methods.toposort
#     toporank = graph_methods.toporank
#     independent_components = graph_methods.independent_components
#     bottoms = graph_methods.bottoms
#     tops = graph_methods.tops
#     non_bottoms = graph_methods.non_bottoms
#     non_tops = graph_methods.non_tops

# class MetaMethods:
#     # meta_irreducibles = meta_methods.meta_irreducibles
#     # meta_downsets = meta_methods.meta_downsets
#     # meta_endomorphisms = meta_methods.meta_endomorphisms
#     # meta_JE = meta_methods.meta_JE
#     # meta_JJ = meta_methods.meta_JJ
#     # upside_down = meta_methods.upside_down
#     # power = meta_methods.power
#     pass

# class TestingMethods:
#     # _test_iters_diff = testing_methods._test_iters_diff
#     # _test_iters = testing_methods._test_iters
#     # _test_counts = testing_methods._test_counts
#     # _test_summary = testing_methods._test_summary
#     # _test_assert_distributive = testing_methods._test_assert_distributive
#     # test_iter_f_monotone = testing_methods.test_iter_f_monotone
#     # test_iter_f_monotone_bottom = testing_methods.test_iter_f_monotone_bottom
#     # test_iter_f_lub = testing_methods.test_iter_f_lub
#     # test_iter_f_lub_pairs = testing_methods.test_iter_f_lub_pairs
#     # test_iter_f_lub_distributive = testing_methods.test_iter_f_lub_distributive
#     # test_count_f_lub_distributive = testing_methods.test_count_f_lub_distributive
#     pass

# class BinaryOperatorMethods:
#     # add_poset = binary_operator_methods.add_poset
#     # mul_poset = binary_operator_methods.mul_poset
#     # or_poset = binary_operator_methods.or_poset
#     # and_poset = binary_operator_methods.and_poset
#     # add_number = binary_operator_methods.add_number
#     # mul_number = binary_operator_methods.mul_number
#     # or_number = binary_operator_methods.or_number
#     # and_number = binary_operator_methods.and_number
#     # _operation_number = binary_operator_methods._operation_number
#     pass

# class EndomorphismMethods:
#     iter_f_all = endomorphisms.iter_f_all
#     num_f_all = endomorphisms.num_f_all
#     iter_f_all_bottom = endomorphisms.iter_f_all_bottom
#     num_f_all_bottom = endomorphisms.num_f_all_bottom
#     f_is_monotone = endomorphisms.f_is_monotone
#     f_meet = endomorphisms.f_meet
#     _as_external_lattice = endomorphisms._as_external_lattice
#     iter_f_monotone_bruteforce = endomorphisms.iter_f_monotone_bruteforce
#     iter_f_monotone_bottom_bruteforce = endomorphisms.iter_f_monotone_bottom_bruteforce
#     iter_f_monotone = endomorphisms.iter_f_monotone
#     iter_f_lub_bruteforce = endomorphisms.iter_f_lub_bruteforce
#     iter_f_monotone_restricted = endomorphisms.iter_f_monotone_restricted
#     _iter_f_monotone_restricted = endomorphisms._iter_f_monotone_restricted
#     _toposort_children = endomorphisms._toposort_children
#     iter_f_monotone_bottom = endomorphisms.iter_f_monotone_bottom
#     irreducible_components = endomorphisms.irreducible_components
#     _interpolate_funcs = endomorphisms._interpolate_funcs
#     iter_f_irreducibles_monotone_bottom = endomorphisms.iter_f_irreducibles_monotone_bottom
#     iter_f_irreducibles_monotone = endomorphisms.iter_f_irreducibles_monotone
#     f_is_lub = endomorphisms.f_is_lub
#     f_is_lub_pairs = endomorphisms.f_is_lub_pairs
#     iter_f_lub_pairs_bruteforce = endomorphisms.iter_f_lub_pairs_bruteforce
#     iter_f_lub_pairs = endomorphisms.iter_f_lub_pairs
#     iter_f_lub = endomorphisms.iter_f_lub
#     num_f_lub_pairs = endomorphisms.num_f_lub_pairs
#     count_f_lub_pairs_bruteforce = endomorphisms.count_f_lub_pairs_bruteforce
#     num_f_lub = endomorphisms.num_f_lub
#     count_f_lub = endomorphisms.count_f_lub
#     count_f_lub_bruteforce = endomorphisms.count_f_lub_bruteforce
#     f_is_lub_of_irreducibles = endomorphisms.f_is_lub_of_irreducibles

#     def iter_f_lub_distributive(self):
#         pass

#     def count_f_lub_distributive(self):
#         pass

#         def num(i: int):
#             pass

# class GenerationMethods:
#     all_latices = generation.all_latices
#     iter_all_latices = generation.iter_all_latices
#     random_poset = generation.random_poset
#     random_lattice_czech = generation.random_lattice_czech

# class InitializationMethods:

#     # total = initialization.total
#     # powerset = initialization.powerset
#     # Mn = initialization.Mn
#     # from_parents = initialization.from_parents
#     # from_children = initialization.from_children
#     # from_down_edges = initialization.from_down_edges
#     # from_up_edges = initialization.from_up_edges
#     # from_lambda = initialization.from_lambda
#     # child_to_dist = initialization.child_to_dist
