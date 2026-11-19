import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import calc_hours
class HoursTests(unittest.TestCase):
    def test_regular_shift(self): self.assertEqual(calc_hours('09:00','17:30',30),(8.0,0))
    def test_overtime(self): self.assertEqual(calc_hours('09:00','18:30',30),(9.0,1.0))
    def test_overnight(self): self.assertEqual(calc_hours('22:00','06:00',0),(8.0,0))
    def test_long_break(self): self.assertEqual(calc_hours('09:00','17:00',60),(7.0,0))
if __name__=='__main__':unittest.main()
