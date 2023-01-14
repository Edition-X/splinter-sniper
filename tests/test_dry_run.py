import unittest
import sys
sys.path.insert(0, '..')
from main import check_dry_run

class TestCheckDryRun(unittest.TestCase):
    def test_dry_run_enabled(self):
        # Simulate command line arguments
        sys.argv = ["main.py", "--dry-run"]
        # Call the function
        dry_run = check_dry_run()
        # Assert that dry_run variable is set to 1
        self.assertEqual(dry_run, 1)
        # Assert that the dry_run_transactions.txt file is created

    def test_dry_run_disabled(self):
        # Simulate command line arguments
        sys.argv = ["main.py"]
        # Call the function
        dry_run = check_dry_run()
        # Assert that dry_run variable is set to 0
        self.assertEqual(dry_run, 0)

if __name__ == '__main__':
    unittest.main()

