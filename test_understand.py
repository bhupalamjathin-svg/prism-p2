from understand import understand


TEST_CASES = [
    (
        "My battery dies really fast",
        "BATTERY_EXCESSIVE_DRAIN"
    ),

    (
        "My battery is draining quickly",
        "BATTERY_EXCESSIVE_DRAIN"
    ),

    (
        "My phone is very slow",
        "DEVICE_SLOW_PERFORMANCE"
    ),

    (
        "My phone keeps lagging",
        "DEVICE_SLOW_PERFORMANCE"
    ),

    (
        "WiFi keeps disconnecting",
        "WIFI_CONNECTION_PROBLEM"
    ),

    (
        "My screen is flickering",
        "DISPLAY_FLICKERING"
    ),

    (
        "battery",
        None
    ),

    (
        "phone problem",
        None
    ),

    (
        "Samsung is acting weird",
        None
    ),
]


def run_tests():

    passed = 0

    print("\nRunning P2 Neural Tests\n")

    for complaint, expected_id in TEST_CASES:

        result = understand(complaint)

        actual_id = result["canonical_id"]

        if expected_id == actual_id:
            print(f"PASS  | {complaint}")
            passed += 1
        else:
            print(
                f"FAIL  | {complaint}"
            )

            print(
                f"       Expected: {expected_id}"
            )

            print(
                f"       Got:      {actual_id}"
            )

    total = len(TEST_CASES)

    print("\n" + "=" * 50)
    print(f"Passed: {passed}/{total}")
    print("=" * 50)

    return passed == total


if __name__ == "__main__":

    success = run_tests()

    if not success:
        raise SystemExit(1)
