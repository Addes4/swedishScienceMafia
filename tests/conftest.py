def pytest_configure(config):
    config.addinivalue_line("markers", "slow: an end-to-end run that takes more than a few seconds")
