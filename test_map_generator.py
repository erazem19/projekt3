import unittest

from map_generator import START, bfs_path, generate_map


class MapGeneratorTests(unittest.TestCase):
    def test_generated_map_connects_start_to_end(self):
        result = generate_map(width=60, height=35, room_count=14, connectivity=20, seed=1234)
        self.assertTrue(result.path)
        self.assertEqual(result.grid[result.start[1]][result.start[0]], START)
        self.assertTrue(bfs_path(result.grid, result.start, result.end))

    def test_generation_is_repeatable_with_seed(self):
        first = generate_map(seed=42)
        second = generate_map(seed=42)
        self.assertEqual(first.grid, second.grid)
        self.assertEqual(first.start, second.start)
        self.assertEqual(first.end, second.end)


if __name__ == "__main__":
    unittest.main()
