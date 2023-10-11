from unittest import TestCase

from utils.utils import prepare_final_results_dictionary, store_module_results_in_database


class TestPrepareFinalResultsDictionary:
    def test_prepare_final_results_dictionary_complete(self, test_redis_db_results_complete):
        expected_results = {
            "target1": {
                "phase1": {"module1": ["result1", "result2"], "module2": ["result3"]}
            },
            "target2": {"phase1": {"module1": ["result4"], "module2": []}},
        }
        result = prepare_final_results_dictionary()
        result["target1"]["phase1"]["module1"].sort()

        # assertion
        TestCase().assertDictEqual(result, expected_results)

    def test_prepare_final_results_dictionary_only_targets(self, test_redis_db_results_only_targets):
        expected_results = {
            "target1": {},
            "target2": {},
        }
        result = prepare_final_results_dictionary()

        # assertion
        TestCase().assertDictEqual(result, expected_results)


class TestStoreModuleResultsInDatabase:
    def test_store_module_results_in_database(self, test_redis_client):
        expected_result_1 = [b"result1"]
        expected_result_2 = {b"result1", b"result2"}
        expected_result_3 = {b"result1", b"result2", b"result3"}

        store_module_results_in_database("target1", {0: "result1"}, "phase1", "module1")
        store_module_results_in_database("target1", {0: "result1"}, "phase1", "module2")
        store_module_results_in_database("target1", {1: "result2"}, "phase1", "module2")
        store_module_results_in_database("target2", {0: "result1"}, "phase1", "module1")
        store_module_results_in_database("target2", {1: "result2"}, "phase1", "module1")
        store_module_results_in_database("target2", {2: "result3"}, "phase1", "module1")

        keys_1 = test_redis_client.keys("target1|phase1|module1|*")
        keys_2 = test_redis_client.keys("target1|phase1|module2|*")
        keys_3 = test_redis_client.keys("target2|phase1|module1|*")

        result_1 = test_redis_client.mget(keys_1)
        result_2 = set(test_redis_client.mget(keys_2))
        result_3 = set(test_redis_client.mget(keys_3))

        assert result_1 == expected_result_1
        # list of byte-type values cannot be sorted that's why we use set
        TestCase().assertSetEqual(result_2, expected_result_2)
        TestCase().assertSetEqual(result_3, expected_result_3)
