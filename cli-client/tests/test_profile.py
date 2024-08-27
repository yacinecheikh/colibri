from libtest import run, create_profile, create_minimal_profile


def test_create_profile():
    create_minimal_profile("test-profile")
    assert run("test-profile", "list-servers") == ""

def test_base_profile():
    create_profile("test-profile")
    assert run("test-profile", "list-trusted-servers") == "http://localhost:8000\n"

