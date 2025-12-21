import sys

from PDA import PDA_Controller


def run_cases_and_print() -> int:
	# Hardcoded cases (edit these however you want)
	cases = [
		("minimal valid", "a/b/c", "String Accepted!", None),
		("n=2 valid", "aa/bb/cc", "String Accepted!", None),
		("extra A", "aa/b/cc", None, "extra A"),
		("extra b", "a/bb/cc", None, "extra b"),
		("extra c", "aa/bb/ccc", None, "extra c"),
		("invalid char", "a/b/x", None, "Invalid character"),
	]

	passed = 0
	total = len(cases)

	print("PDA hardcoded test cases")
	print("=" * 60)

	for idx, (name, input_string, expected_exact, expected_contains) in enumerate(cases, start=1):
		pda = PDA_Controller()
		result = pda.process(input_string)

		if expected_exact is not None:
			ok = result == expected_exact
			expected_str = expected_exact
		else:
			ok = expected_contains is not None and (expected_contains in result)
			expected_str = f"contains '{expected_contains}'"

		status = "PASS" if ok else "FAIL"
		print(f"{idx:02d}. {status} | {name}")
		print(f"    input : {input_string}")
		print(f"    result: {result}")
		print(f"    expect: {expected_str}")
		print("-" * 60)

		passed += 1 if ok else 0

	failed = total - passed
	print(f"Summary: {passed}/{total} passed, {failed} failed")
	return 0 if failed == 0 else 1


if __name__ == "__main__":
	# Always print the PASS/FAIL case output.
	# You can still pass --cases; it will be ignored for compatibility.
	if "--cases" in sys.argv:
		sys.argv = [arg for arg in sys.argv if arg != "--cases"]

	raise SystemExit(run_cases_and_print())
