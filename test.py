from run import app
import json
import unittest
import random
import string

class TestCase(unittest.TestCase):
    def __init__(self, route, options):
        self.route=route
        self.options=options
        self.response=self.get_response(f'{route}?{options}')
        self.data=self.response.get_data().decode("utf-8")

    def get_response(self, route):
        tester=app.test_client(self)
        response=tester.get(route)
        return response

    def get_json_data(self):
        self.json_data= json.loads(self.data)

class Index(unittest.TestCase):

    def test_index_page(self):
        testcase=TestCase("/", "")
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")
        

class SingleCharacter(unittest.TestCase):
    def test_good_character(self):
        testcase=TestCase("/api/character/mario", "")
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")

    def test_include_exclude_character_status_failure(self):
        testcase=TestCase("/api/character/mario", "include=test&exclude=test")
        self.assertEquals(testcase.response.status_code, 400)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")

    def test_bad_character(self):
        letters = string.ascii_lowercase
        randomString=''.join(random.choice(letters) for i in range(10))
        testcase=TestCase(f'/api/character/{randomString}', "")
        self.assertEquals(testcase.response.status_code, 404)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")
        self.assertIn(randomString, testcase.data)
    
class AllCharacter(unittest.TestCase):
    def test_all_character_data(self):
        testcase=TestCase("/api/character/all", "")
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")

    def test_include_exclude_all_character(self):
        testcase=TestCase("/api/character/all", "include=test&exclude=test")
        self.assertEquals(testcase.response.status_code, 400)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")

class MoveData(unittest.TestCase):
    def test_move_data(self):
        testcase=TestCase("/api/move/MarioJab1", "")
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")

    def test_include_exclude_move(self):
        testcase=TestCase("/api/move/MarioJab1", "include=test&exclude=test")
        self.assertEquals(testcase.response.status_code, 400)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")

    def test_bad_move(self):
        letters = string.ascii_lowercase
        randomString=''.join(random.choice(letters) for i in range(10))
        testcase=TestCase(f'/api/move/{randomString}', "")
        self.assertEquals(testcase.response.status_code, 404)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")
        self.assertIn(randomString, testcase.data)

class Images(unittest.TestCase):
    def test_get_all_images(self):
        testcase=TestCase("/api/images/MarioJab1", "")
        testcase.get_json_data()
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")
        self.assertEquals(testcase.json_data["imgCount"], len(testcase.json_data["urls"]))
    
    def test_single_frame(self):
        randFrame=random.randrange(2,9)
        testcase=TestCase("/api/images/MarioJab1", f'frame={randFrame}')
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")
        self.assertIn(f'https://ultimate-hitboxes.s3.amazonaws.com/frames/01_mario/MarioJab1/{randFrame}.png', testcase.data)

    def test_start_frame(self):
        testcase=TestCase("/api/images/MarioJab1", "startFrame=5")
        testcase.get_json_data()
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")
        self.assertEquals(testcase.json_data["imgCount"], len(testcase.json_data["urls"]))
        self.assertEquals(testcase.json_data["frames"][0], 5)

    def test_end_frame(self):
        testcase=TestCase("/api/images/MarioJab1", "endFrame=10")
        testcase.get_json_data()
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")
        self.assertEquals(testcase.json_data["imgCount"], len(testcase.json_data["urls"]))
        self.assertEquals(testcase.json_data["frames"][0], 1)
        self.assertEquals(testcase.json_data["frames"][-1], 10)

    def test_start_end_frame(self):
        testcase=TestCase("/api/images/MarioJab1", "startFrame=5&endFrame=10")
        testcase.get_json_data()
        self.assertEquals(testcase.response.status_code, 200)
        self.assertEquals(testcase.response.content_type, "application/json")
        self.assertEquals(testcase.json_data["imgCount"], len(testcase.json_data["urls"]))
        self.assertEquals(testcase.json_data["frames"][0], 5)
        self.assertEquals(testcase.json_data["frames"][-1], 10)

    def test_start_larger_end_frame(self):
        testcase=TestCase("/api/images/MarioJab1", "startFrame=15&endFrame=10")
        self.assertEquals(testcase.response.status_code, 400)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")

    def test_invalid_move(self):
        letters = string.ascii_lowercase
        randomString=''.join(random.choice(letters) for i in range(10))
        testcase=TestCase(f'/api/images/{randomString}', "")
        self.assertEquals(testcase.response.status_code, 404)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")
        self.assertIn(randomString, testcase.data)
        

class MiscTests(unittest.TestCase):
    def test_bad_url(self):
        testcase=TestCase("/test", "")
        self.assertEquals(testcase.response.status_code, 404)
        self.assertEquals(testcase.response.content_type, "text/html; charset=utf-8")



if __name__ == "__main__":
    unittest.main()
