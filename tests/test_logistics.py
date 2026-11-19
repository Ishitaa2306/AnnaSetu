"""
Unit & Integration Test Suite for Anna Setu Karnataka — Logistics & Agent 3 Enhancements.
Tests route recommendation, hybrid transport dispatch, volunteer cancellation & re-dispatch,
fleet onboarding, and volunteer milestone recognition.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime, timezone, timedelta
import tools as t
import database as db
from agents import run_donation_workflow, run_logistics_workflow


class LogisticsTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_schema()

    def test_01_bengaluru_route_estimation(self):
        """Test corridor routing, distance and transit time between Bengaluru hubs."""
        route = t.estimate_bengaluru_route("Indiranagar 100 Ft Rd, Bengaluru", "Koramangala 5th Block, Bengaluru")
        self.assertIn("distance_km", route)
        self.assertIn("transit_mins", route)
        self.assertIn("corridor", route)
        self.assertIn("gmaps_url", route)
        self.assertGreater(route["distance_km"], 1.0)
        self.assertGreater(route["transit_mins"], 10)
        self.assertTrue("google.com/maps" in route["gmaps_url"])

    def test_02_hybrid_logistics_volunteer_assignment(self):
        """Test that small to medium loads (<= 80 meals) are assigned to community volunteers."""
        volunteers = t.get_available_volunteers()
        self.assertGreater(len(volunteers), 0)
        
        # Test creating an assignment with route
        aid = t.create_assignment(
            match_id=1,
            volunteer_id=volunteers[0]["id"],
            transport_provider_id=None,
            pickup_location="Indiranagar, Bengaluru",
            delivery_location="Koramangala, Bengaluru",
            pickup_time_scheduled=datetime.now(timezone.utc) + timedelta(hours=2),
            transport_mode="volunteer"
        )
        asgn = t.get_assignment(aid)
        self.assertIsNotNone(asgn)
        self.assertEqual(asgn["transport_mode"], "volunteer")
        self.assertGreater(float(asgn.get("estimated_distance_km") or 0), 0)

    def test_03_volunteer_cancellation_and_automatic_redispatch(self):
        """Test that when a volunteer declines/cancels, Agent 3 re-dispatches to an alternative resource."""
        volunteers = t.get_available_volunteers()
        self.assertGreaterEqual(len(volunteers), 2)
        
        first_vol = volunteers[0]
        aid = t.create_assignment(
            match_id=1,
            volunteer_id=first_vol["id"],
            transport_provider_id=None,
            pickup_location="Indiranagar, Bengaluru",
            delivery_location="Koramangala, Bengaluru",
            pickup_time_scheduled=datetime.now(timezone.utc) + timedelta(hours=2),
            transport_mode="volunteer"
        )
        
        # Cancel / Decline
        result = t.reassign_logistics_assignment(aid, "Flat tyre on vehicle", triggered_by="volunteer_decline")
        self.assertTrue(result["success"])
        self.assertNotEqual(result["new_assignment_id"], aid)
        
        # Old assignment should be cancelled
        old_asgn = t.get_assignment(aid)
        self.assertEqual(old_asgn["status"], "cancelled")
        self.assertIn("Flat tyre", old_asgn.get("cancellation_reason", ""))
        
        # New assignment should be active
        new_asgn = t.get_assignment(result["new_assignment_id"])
        self.assertIsNotNone(new_asgn)
        self.assertNotEqual(new_asgn["volunteer_id"], first_vol["id"])

    def test_04_volunteer_registration(self):
        """Test public onboarding of a new community volunteer."""
        new_vid = t.register_new_volunteer({
            "full_name": "Test Logistics Rescuer",
            "phone": "9988776655",
            "city": "Bengaluru",
            "address": "Malleshwaram, Bengaluru",
            "locality": "Malleshwaram",
            "vehicle_type": "bike",
            "vehicle_capacity_meals": 35
        })
        self.assertIsInstance(new_vid, int)
        self.assertGreater(new_vid, 0)

    def test_05_transport_partner_registration(self):
        """Test registration of a commercial or NGO fleet provider."""
        tpid = t.register_new_transport_partner({
            "name": "Green City Rapid Cargo",
            "vehicle_type": "Tata Ace",
            "capacity_meals": 500,
            "city": "Bengaluru",
            "locality": "Outer Ring Road",
            "service_type": "Commercial",
            "base_rate": 200,
            "per_km_rate": 18,
            "cost_per_trip": 300,
            "contact_phone": "9811223344"
        })
        self.assertIsInstance(tpid, int)
        self.assertGreater(tpid, 0)

    def test_06_volunteer_profile_stats_and_badge(self):
        """Test calculation of volunteer milestones, verified hours, and recognition rank."""
        volunteers = t.get_all_volunteers()
        self.assertGreater(len(volunteers), 0)
        target_vol = volunteers[0]
        
        stats = t.get_volunteer_profile_stats(target_vol["id"])
        self.assertIn("verified_hours", stats)
        self.assertIn("badge_level", stats)
        self.assertIn("reimbursement_due", stats)
        self.assertIn(stats["badge_level"], ["Bronze Hero", "Silver Champion", "Gold Guardian"])

    def test_07_live_telemetry_and_destination_arrival(self):
        """Test live GPS checkpoint broadcast and driver destination arrival detection."""
        volunteers = t.get_available_volunteers()
        aid = t.create_assignment(
            match_id=1,
            volunteer_id=volunteers[0]["id"],
            transport_provider_id=None,
            pickup_location="Indiranagar, Bengaluru",
            delivery_location="Koramangala, Bengaluru",
            pickup_time_scheduled=datetime.now(timezone.utc) + timedelta(hours=2),
            transport_mode="volunteer"
        )

        # 1. Driver in transit checkpoint
        track1 = t.update_driver_live_tracking(aid, "in_transit", "Crossing Domlur Flyover", remaining_mins=8)
        self.assertTrue(track1["success"])
        self.assertEqual(track1["status"], "in_transit")
        self.assertFalse(track1["reached_destination"])

        # Check telemetry reader
        live_telemetry = t.get_live_trip_tracking(aid)
        self.assertIsNotNone(live_telemetry)
        self.assertEqual(live_telemetry["status"], "in_transit")
        self.assertFalse(live_telemetry["has_reached_destination"])
        self.assertEqual(live_telemetry["current_checkpoint"], "Crossing Domlur Flyover")

        # 2. Driver arrived at destination gate
        track2 = t.update_driver_live_tracking(aid, "arrived_destination", "Driver arrived at shelter gate", remaining_mins=0)
        self.assertTrue(track2["success"])
        self.assertTrue(track2["reached_destination"])

        telemetry_arrived = t.get_live_trip_tracking(aid)
        self.assertTrue(telemetry_arrived["has_reached_destination"])
        self.assertEqual(telemetry_arrived["status"], "arrived_destination")
        self.assertEqual(telemetry_arrived["progress_pct"], 95)


if __name__ == "__main__":
    unittest.main()
