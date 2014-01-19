#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import unittest
from nose.tools import ok_, eq_
from mock import Mock

from avalon_python.control_structures.sea_battle import Warship

class TestWarship(unittest.TestCase):
    def setUp(self):
        # shortcuts
        self.COMP_NORMAL = Warship.compartment_state.NORMAL
        self.COMP_DESTR = Warship.compartment_state.DESTROYED

    # __init__
    def test_create_corvette(self):
        warship = Warship(0, 0, 0, 0)

        eq_(warship._type, Warship.warship_types.CORVETTE)

    def test_create_frigate(self):
        warship = Warship(0, 0, 1, 0)

        eq_(warship._type, Warship.warship_types.FRIGATE)

    def test_create_destroyer(self):
        warship = Warship(0, 0, 2, 0)

        eq_(warship._type, Warship.warship_types.DESTROYER)

    def test_create_battlecruiser(self):
        warship = Warship(0, 0, 3, 0)

        eq_(warship._type, Warship.warship_types.BATTLECRUISER)


    # determine_length
    def test_determine_length_corvette(self):
        eq_(Warship.determine_length(0, 0, 0, 0), 1)

    def test_determine_length_hor_frigate(self):
        eq_(Warship.determine_length(0, 0, 1, 0), 2)

    def test_determine_length_hor_destroyer(self):
        eq_(Warship.determine_length(0, 0, 2, 0), 3)

    def test_determine_length_hor_battlecruiser(self):
        eq_(Warship.determine_length(0, 0, 3, 0), 4)

    def test_determine_length_ver_frigate(self):
        eq_(Warship.determine_length(0, 0, 0, 1), 2)

    def test_determine_length_ver_destroyer(self):
        eq_(Warship.determine_length(0, 0, 0, 2), 3)

    def test_determine_length_ver_battlecruiser(self):
        eq_(Warship.determine_length(0, 0, 0, 3), 4)


    # build_compartments
    def test_build_compartments_hor_corvette(self):
        compartments = Warship.build_compartments(0, 0, 0, 0)
        eq_(compartments, [[0, 0, self.COMP_NORMAL],])

    def test_build_compartments_hor_frigate(self):
        compartments = Warship.build_compartments(0, 0, 1, 0)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [1, 0, self.COMP_NORMAL], ])

    def test_build_compartments_hor_destroyer(self):
        compartments = Warship.build_compartments(0, 0, 2, 0)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [1, 0, self.COMP_NORMAL], [2, 0, self.COMP_NORMAL],])

    def test_build_compartments_ver_battlecruiser(self):
        compartments = Warship.build_compartments(0, 0, 3, 0)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [1, 0, self.COMP_NORMAL], [2, 0, self.COMP_NORMAL], [3, 0, self.COMP_NORMAL],])

    def test_build_compartments_ver_frigate(self):
        compartments = Warship.build_compartments(0, 0, 0, 1)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], ])

    def test_build_compartments_ver_destroyer(self):
        compartments = Warship.build_compartments(0, 0, 0, 2)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],])

    def test_build_compartments_ver_battlecruiser(self):
        compartments = warship.build_compartments(0, 0, 0, 3)
        eq_(compartments, [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL], [0, 3, self.COMP_NORMAL],])

    # determine_type
    def test_determine_type_hor_corvette(self):
        warship_type = Warship.determine_type(0, 0, 0, 0)
        eq_(warship_type, Warship.warship_types.CORVETTE)

    def test_determine_type_hor_frigate(self):
        warship_type = Warship.determine_type(0, 0, 1, 0)
        eq_(warship_type, Warship.warship_types.FRIGATE)

    def test_determine_type_hor_destroyer(self):
        warship_type = Warship.determine_type(0, 0, 2, 0)
        eq_(warship_type, Warship.warship_types.DESTROYER)

    def test_determine_type_ver_battlecruiser(self):
        warship_type = Warship.determine_type(0, 0, 3, 0)
        eq_(warship_type, Warship.warship_types.BATTLECRUISER)

    def test_determine_type_ver_frigate(self):
        warship_type = Warship.determine_type(0, 0, 0, 1)
        eq_(warship_type, Warship.warship_types.FRIGATE)

    def test_determine_type_ver_destroyer(self):
        warship_type = Warship.determine_type(0, 0, 0, 2)
        eq_(warship_type, Warship.warship_types.DESTROYER)

    def test_build_compartments_ver_battlecruiser(self):
        compartments = Warship.determine_type(0, 0, 0, 3)
        eq_(compartments, Warship.warship_types.BATTLECRUISER)

    # check_hull_condition
    def test_check_hull_condition_normal_corvette(self):
        compartments = [[0, 0, 1],]
        eq_(Warship.check_hull_condition(compartments), Warship.hull_state.NORMAL)

    def test_check_hull_condition_destroyed_corvette(self):
        compartments = [[0, 0, 0],]
        eq_(Warship.check_hull_condition(compartments), Warship.hull_state.DESTROYED)

    def test_check_hull_condition_normal_destroyer(self):
        compartments = [[0, 0, 1], [0, 1, 1], [0, 2, 1],]
        eq_(Warship.check_hull_condition(compartments), Warship.hull_state.NORMAL)

    def test_check_hull_condition_damaged_destroyer(self):
        compartments = [[0, 0, 0], [0, 1, 1], [0, 2, 1],]
        eq_(Warship.check_hull_condition(compartments), Warship.hull_state.DAMAGED)

    def test_check_hull_condition_destroyed_destroyer(self):
        compartments = [[0, 0, 0], [0, 1, 0], [0, 2, 0],]
        eq_(Warship.check_hull_condition(compartments), Warship.hull_state.DESTROYED)

    # collide
    def test_collide_hit_1(self):
        compartments = [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],]
        eq_(Warship.collide(compartments, 0, 0), Warship.collision_status.HIT)

    def test_collide_hit_2(self):
        compartments = [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],]
        eq_(Warship.collide(compartments, 0, 1), Warship.collision_status.HIT)

    def test_collide_hit_3(self):
        compartments = [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],]
        eq_(Warship.collide(compartments, 0, 2), Warship.collision_status.HIT)

    def test_collide_already_hit(self):
        compartments = [[0, 0, self.COMP_DESTR], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],]
        eq_(Warship.collide(compartments, 0, 0), Warship.collision_status.ALREADY_HIT)

    def test_collide_miss(self):
        compartments = [[0, 0, self.COMP_NORMAL], [0, 1, self.COMP_NORMAL], [0, 2, self.COMP_NORMAL],]
        eq_(Warship.collide(compartments, 5, 5), Warship.collision_status.MISS)



