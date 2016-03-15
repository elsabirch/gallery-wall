import unittest
import server
import utilities
import doctest
import seed_database as sd
import arrange as ar
# from flask import session

def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    # tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class UtilitiesParserFunctionsTestCase(unittest.TestCase):

    def test_to_clean_string_from_input(self):

        # Case for string already clean
        test_in = 'foo13ar'
        expect_out = 'foo13ar'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string not clean
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo13ardroptables'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string only unclean
        test_in = '&*#%;+'
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string empty
        test_in = ''
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string unclean and too long
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 3),
                         expect_out)

    def test_to_float_from_input(self):

        # Case for spaces
        test_in = '  13 '
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for other characters arround
        test_in = 'foo13*ar'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for decimals
        test_in = '13.14'
        expect_out = 13.14
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero pad
        test_in = '00013'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for empty
        test_in = ''
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for all unclean
        test_in = 'juihiuhr&&*@'
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for negative
        test_in = '-13.0 '
        expect_out = -13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for fractional
        test_in = '0.13'
        expect_out = 0.13
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero
        test_in = '-0.0 '
        expect_out = 0.0
        self.assertAlmostEqual(utilities.to_float_from_input(test_in),
                               expect_out)


class NavigationServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = os.environ['FLASK_APP_SECRET_KEY']

    def test_navigation_logged_out(self):

        result = self.client.get('/navigation')
        self.assertIn('Galleries', result.data)
        self.assertIn('Walls', result.data)
        self.assertNotIn('Curate', result.data)
        self.assertNotIn('Upload', result.data)

class NavigationServerRoutesLoggedInTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = os.environ['FLASK_APP_SECRET_KEY']

        with self.client as c:
            with c.session_transaction() as se:
                se['user_id'] = 13
                se['username'] = 'foo'

    def test_navigation_logged_in(self):

        result = self.client.get('/navigation')
        self.assertIn('Galleries', result.data)
        self.assertIn('Walls', result.data)
        self.assertIn('Curate', result.data)
        self.assertIn('Upload', result.data)

    # tear down by logging out
    def tearDown(self):

        with self.client as c:
            with c.session_transaction() as se:
                se.pop('user_id')
                se.pop('username')


class LoginServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def test_login_signup(self):
        result = self.client.get('/login')
        self.assertIn('Username', result.data)
        self.assertIn('Email', result.data)
        self.assertIn('Password', result.data)


class WorkspaceInitTestCase(unittest.TestCase):

    # Test Gallery (11)
    # 11 | 49, 42, 41
    # 41  |   1   |   4   |   4   |   love_4x4.jpg    |   love    |   @elsabirch  |   public
    # 42  |   1   |   6   |   6   |   banana_6x6.jpg  |   banana  |   @elsabirch  |   public
    # 49  |   1   |   10  |   8   |   wave_10x8.jpg   |   wave    |   @elsabirch  |   public

    def setUp(self):

        seed_files = {
            'users': "seed/seed_test_users.txt",
            'pictures': "seed/seed_test_pictures.txt",
            'galleries': "seed/seed_test_galleries.txt",
            'memberships': "seed/seed_test_memberships.txt",
            'walls': "seed/seed_test_walls.txt",
            'placements': "seed/seed_test_placements.txt",
        }

        sd.seed_all(seed_files)

    def test_init(self):

        wkspc = ar.Workspace(11)

        self.assertEqual(wkspc.gallery_id, 11)
        self.assertEqual(wkspc.len, 3)
        self.assertEqual(wkspc.margin, 2)

        self.assertIn(41, wkspc.pics)
        self.assertIn(42, wkspc.pics)
        self.assertIn(49, wkspc.pics)

        # All pics are instance of correct class
        for p in wkspc.pics:
            self.assertTrue(isinstance(wkspc.pics[p], ar.Pic))

        # Correct number of pics
        self.assertEqual(len(wkspc.pics), 3)

if __name__ == "__main__":
    unittest.main()
