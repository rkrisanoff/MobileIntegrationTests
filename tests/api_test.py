import unittest

import pytest
import requests
import psycopg2

default_schema = "studhelper"

api_base = "http://localhost:8080"

base_headers = {"Content-Type": "application/json"}

users = ({"login": "vasya", "password": "qwerty", "fullName": "Arturito Sanchez"},
         {"login": "anton", "password": "anton", "fullName": "Arturito Sanchez"},
         {"login": "artem", "password": "artem", "fullName": "Arturito Sanchez"},
         {"login": "pawel", "password": "pawel", "fullName": "Alice"},
         {"login": "motherfucker", "password": "motherfucker", "fullName": "Azdrubael Vect"},
         )


class ApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Perform any setup tasks before each test
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="dma-test",
            user="drukhary",
            password="142857"
        )

        cursor = connection.cursor()

        # Выполнение необходимых запросов или настроек перед каждым тестом
        cursor.execute(f"TRUNCATE TABLE {default_schema}.user CASCADE;")
        cursor.execute(f"TRUNCATE TABLE {default_schema}.group CASCADE;")
        cursor.execute(f"TRUNCATE TABLE {default_schema}.queue CASCADE;")
        cursor.execute(f"TRUNCATE TABLE {default_schema}.queue_student CASCADE;")
        cursor.execute(f"ALTER SEQUENCE {default_schema}.user_id_seq RESTART WITH 1;")
        cursor.execute(f"ALTER SEQUENCE {default_schema}.group_id_seq RESTART WITH 1;")
        cursor.execute(f"ALTER SEQUENCE {default_schema}.queue_id_seq RESTART WITH 1;")

        connection.commit()

    @classmethod
    def tearDownClass(cls):
        # Perform any setup tasks before each test
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="dma-test",
            user="drukhary",
            password="142857"
        )

        cursor = connection.cursor()

        # Выполнение необходимых запросов или настроек перед каждым тестом
        # cursor.execute(f"TRUNCATE TABLE {default_schema}.user CASCADE;")
        # cursor.execute(f"TRUNCATE TABLE {default_schema}.group CASCADE;")
        # cursor.execute(f"TRUNCATE TABLE {default_schema}.queue CASCADE;")
        # cursor.execute(f"TRUNCATE TABLE {default_schema}.queue_student CASCADE;")
        # cursor.execute(f"ALTER SEQUENCE {default_schema}.user_id_seq RESTART WITH 1;")
        # cursor.execute(f"ALTER SEQUENCE {default_schema}.group_id_seq RESTART WITH 1;")
        # cursor.execute(f"ALTER SEQUENCE {default_schema}.queue_id_seq RESTART WITH 1;")

        connection.commit()


class ApiTestUsers(ApiTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @pytest.mark.order(1)
    def test_login_non_existing_users(self):
        for user_creds in users:
            response = requests.get(url=f"{api_base}/users/login",
                                    headers={**base_headers},
                                    auth=(user_creds["login"], user_creds["password"])
                                    )

            assert response.status_code != 200

    @pytest.mark.order(2)
    def test_register_users(self):
        for user_creds in users:
            response = requests.post(url=f"{api_base}/users/register",
                                     headers={**base_headers},
                                     json={**user_creds}
                                     )

            assert response.status_code == 200

    @pytest.mark.order(3)
    def test_login_existing_users(self):
        for user_creds in users:
            response = requests.get(url=f"{api_base}/users/login",
                                    headers={**base_headers},
                                    auth=(user_creds["login"], user_creds["password"])
                                    )

            assert response.status_code == 200

    @pytest.mark.order(4)
    def test_register_already_existing_users(self):
        for user_creds in users:
            response = requests.post(url=f"{api_base}/users/register",
                                     headers={**base_headers},
                                     json={**user_creds}
                                     )

            assert response.status_code != 200


@pytest.mark.order(after="ApiTestUsers")
class ApiTestGroups(ApiTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for user_creds in users:
            assert requests.post(url=f"{api_base}/users/register",
                                 headers={**base_headers},
                                 json={**user_creds}
                                 ).status_code == 200

    @pytest.mark.order(1)
    def test_get_non_existing_group_creds(self):
        for user in users:
            response = requests.get(url=f"{api_base}/group",
                                    headers={**base_headers},
                                    auth=(user["login"], user["password"]),
                                    )
            assert response.status_code != 200

    @pytest.mark.order(after="ApiTestGroups::test_get_group_creds_failed")
    def test_create_groups(self):
        for user in users[0:3]:
            response = requests.post(url=f"{api_base}/group",
                                     headers={**base_headers},
                                     auth=(user["login"], user["password"]),
                                     json={"groupName": "CoolGroup"}
                                     )
            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestGroups::test_create_groups")
    def test_get_group_creds(self):
        for user in users[0:3]:
            response = requests.get(url=f"{api_base}/group",
                                    headers={**base_headers},
                                    auth=(user["login"], user["password"]),
                                    )
            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestGroups::test_get_group_creds")
    def test_create_existing_groups(self):
        for user in users[0:3]:
            response = requests.post(url=f"{api_base}/group",
                                     headers={**base_headers},
                                     auth=(user["login"], user["password"]),
                                     json={"groupName": "CoolGroup"}
                                     )
            assert response.status_code != 200

    @pytest.mark.order(after="ApiTestGroups::test_create_existing_groups")
    def test_delete_groups(self):
        for user in users[1:3]:
            response = requests.delete(url=f"{api_base}/group",
                                       headers={**base_headers},
                                       auth=(user["login"], user["password"]),
                                       json={}
                                       )

            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestGroups::test_delete_groups")
    def test_delete_non_existing_groups(self):
        for user in users[1:3]:
            response = requests.delete(url=f"{api_base}/group",
                                       headers={**base_headers},
                                       auth=(user["login"], user["password"]),
                                       json={}
                                       )

            assert response.status_code != 200

    @pytest.mark.order(after="ApiTestGroups::test_delete_non_existing_groups")
    def test_join_group(self):
        response = requests.get(url=f"{api_base}/group",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )
        assert response.status_code == 200
        invite_code = response.json()["inviteCode"]

        for user in users[1:]:
            response = requests.patch(url=f"{api_base}/group",
                                      headers={**base_headers},
                                      auth=(user["login"], user["password"]),
                                      json={"inviteCode": invite_code}
                                      )

            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestGroups::test_join_group")
    def test_quit_group(self):
        for user in users[3:]:
            response = requests.patch(url=f"{api_base}/group/quit",
                                      headers={**base_headers},
                                      auth=(user["login"], user["password"]),
                                      )

            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestGroups::test_quit_group")
    def test_quit_group_failure(self):
        for user in users[3:]:
            response = requests.patch(url=f"{api_base}/group/quit",
                                      headers={**base_headers},
                                      auth=(user["login"], user["password"]),
                                      )

            assert response.status_code != 200

    @pytest.mark.order(after="ApiTestGroups::test_quit_group_failure")
    def test_delete_groups_without_permission(self):
        for user in users[1:3]:
            response = requests.delete(url=f"{api_base}/group",
                                       headers={**base_headers},
                                       auth=(user["login"], user["password"]),
                                       )

            assert response.status_code != 200


@pytest.mark.order(after="ApiTestGroups")
class ApiTestQueue(ApiTest):
    """
    Test for Queues
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for user_creds in users:
            assert requests.post(url=f"{api_base}/users/register",
                                 headers={**base_headers},
                                 json={**user_creds}
                                 ).status_code == 200
        response = requests.post(url=f"{api_base}/group",
                                 headers={**base_headers},
                                 auth=(users[0]["login"], users[0]["password"]),
                                 json={"groupName": "CoolName"},
                                 )
        assert response.status_code == 200
        invite_code = response.json()["inviteCode"]
        for user_creds in users[1:]:
            assert requests.patch(url=f"{api_base}/group",
                                  headers={**base_headers},
                                  auth=(user_creds["login"], user_creds["password"]),

                                  json={"inviteCode": invite_code}
                                  ).status_code == 200

    def test_create_queue_failure(self):
        for user_creds in users[1:]:
            response = requests.post(url=f"{api_base}/group/queues",
                                     headers={**base_headers},
                                     auth=(user_creds["login"], user_creds["password"]),
                                     json={"queueName": "CoolQueue"}
                                     )
            self.assertNotEqual(response.status_code, 200, "wrong ")

    def test_create_queue(self):
        response = requests.post(url=f"{api_base}/group/queues",
                                 headers={**base_headers},
                                 auth=(users[0]["login"], users[0]["password"]),
                                 json={"queueName": "CoolQueue"}
                                 )

        assert response.status_code == 200

    @pytest.mark.order(after="ApiTestQueue::test_create_queue")
    def test_enter_queue(self):
        response = requests.get(url=f"{api_base}/group/queues",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )

        assert response.status_code == 200
        queues = response.json()["queueList"]
        for user_creds in users[1:]:
            response = requests.patch(url=f"{api_base}/group/queues/{queues[0]['id']}",
                                      headers={**base_headers},
                                      auth=(user_creds["login"], user_creds["password"]),
                                      json={}
                                      )
            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestQueue::test_enter_queue")
    def test_quit_queue(self):
        response = requests.get(url=f"{api_base}/group/queues",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )

        assert response.status_code == 200
        queues = response.json()["queueList"]
        for user_creds in users[3:]:
            response = requests.patch(url=f"{api_base}/group/queues/{queues[0]['id']}/quit",
                                      headers={**base_headers},
                                      auth=(user_creds["login"], user_creds["password"]),
                                      json={}
                                      )
            assert response.status_code == 200

    @pytest.mark.order(after="ApiTestQueue::test_quit_queue")
    def test_quit_queue_failure(self):
        response = requests.get(url=f"{api_base}/group/queues",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )

        assert response.status_code == 200
        queues = response.json()["queueList"]
        for user_creds in users[3:]:
            response = requests.patch(url=f"{api_base}/group/queues/{queues[0]['id']}/quit",
                                      headers={**base_headers},
                                      auth=(user_creds["login"], user_creds["password"]),
                                      json={}
                                      )
            assert response.status_code != 200

    @pytest.mark.order(after="ApiTestQueue::test_quit_queue_failure")
    def test_get_student_in_queue_list(self):
        response = requests.get(url=f"{api_base}/group/queues/{1}",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )

        self.assertEqual(response.status_code, 200)
        queue_creds = response.json()
        self.assertEqual(queue_creds["queueId"], 1)
        self.assertEqual(queue_creds["queueName"], "CoolQueue")
        for user in queue_creds["users"]:
            self.assertEqual(users[user["id"] - 1]["fullName"], user["fullName"])

    @pytest.mark.order(after="ApiTestQueue::test_get_student_in_queue_list")
    def test_get_queues_in_group_list(self):
        response = requests.get(url=f"{api_base}/group/queues",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )
        self.assertEqual(response.status_code, 200)
        queues = response.json()["queueList"]
        self.assertGreater(len(queues), 0)

    @pytest.mark.order(after="ApiTestQueue::test_get_queues_in_group_list")
    def test_delete_queues(self):
        response = requests.delete(url=f"{api_base}/group/queues/{1}",
                                   headers={**base_headers},
                                   auth=(users[0]["login"], users[0]["password"]),
                                   )

        self.assertEqual(response.status_code, 200)

    @pytest.mark.order(after="ApiTestQueue::test_delete_queues")
    def test_get_queues_in_group_empty_list(self):
        response = requests.get(url=f"{api_base}/group/queues",
                                headers={**base_headers},
                                auth=(users[0]["login"], users[0]["password"]),
                                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["queueList"]), 0)


if __name__ == '__main__':
    unittest.main()
