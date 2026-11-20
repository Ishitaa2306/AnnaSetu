import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import database as db
import tools as t

class AuthOnboardingTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_schema()

    def test_01_user_signup_and_login(self):
        """Test registration of volunteer with mobile number & password, then logging in."""
        test_phone = "9900112233"
        test_pass = "SecurePass@123"
        
        # Cleanup if leftover from earlier run
        with db.engine.connect() as conn:
            conn.execute(db.text("DELETE FROM as_volunteers WHERE phone = :p"), {"p": test_phone})
            conn.execute(db.text("DELETE FROM as_users WHERE phone = :p OR username = :p"), {"p": test_phone})
            conn.commit()

        # 1. Check duplicate check before registration
        existing = db.get_user_by_identifier(test_phone)
        self.assertIsNone(existing)

        # 2. Register User Account
        pwd_hash = db.hash_password(test_pass)
        uid = db.create_user({
            "username": test_phone,
            "phone": test_phone,
            "password_hash": pwd_hash,
            "role": "volunteer",
            "full_name": "Test Onboarded Volunteer",
            "email": f"{test_phone}@volunteer.annasetu.org",
            "is_active": True,
            "is_approved": True,
        })
        self.assertGreater(uid, 0)

        # 3. Register Volunteer Profile
        vid = t.register_new_volunteer({
            "user_id": uid,
            "full_name": "Test Onboarded Volunteer",
            "phone": test_phone,
            "city": "Bengaluru",
            "address": "Indiranagar, Bengaluru",
            "locality": "Indiranagar",
            "vehicle_type": "bike",
            "vehicle_capacity_meals": 40,
        })
        self.assertGreater(vid, 0)

        # 4. Authenticate using mobile number and password
        auth_user = db.authenticate(test_phone, test_pass)
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["id"], uid)
        self.assertEqual(auth_user["phone"], test_phone)
        self.assertEqual(auth_user["role"], "volunteer")

        # 5. Authenticate with wrong password should fail
        wrong_auth = db.authenticate(test_phone, "WrongPassword")
        self.assertIsNone(wrong_auth)

        # 6. Check duplicate prevention
        existing_again = db.get_user_by_identifier(test_phone)
        self.assertIsNotNone(existing_again)

        # 7. Check volunteer profile linked
        vol_profile = t.get_volunteer_by_user_id(uid)
        self.assertIsNotNone(vol_profile)
        self.assertEqual(vol_profile["id"], vid)
        self.assertEqual(vol_profile["phone"], test_phone)

        # Cleanup
        with db.engine.connect() as conn:
            conn.execute(db.text("DELETE FROM as_volunteers WHERE phone = :p"), {"p": test_phone})
            conn.execute(db.text("DELETE FROM as_users WHERE id = :uid"), {"uid": uid})
            conn.commit()

    def test_02_seed_demo_accounts_still_work(self):
        """Ensure admin and volunteer_arjun accounts still authenticate without breaking."""
        admin = db.authenticate("admin", "Admin@1234")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

        vol = db.authenticate("volunteer_arjun", "Demo@1234")
        self.assertIsNotNone(vol)
        self.assertEqual(vol["role"], "volunteer")


if __name__ == "__main__":
    unittest.main()
