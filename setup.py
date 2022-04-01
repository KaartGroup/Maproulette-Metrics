import setuptools

setuptools.setup(
    name="maproulette_metrics",
    version="0.0.1",
    packages=["maproulette_metrics"],
    python_requires=">=3.10",
    install_requires=["pandas", "requests", "pyyaml", "more_itertools", "keyring"],
    entry_points={
        "console_scripts": [
            "get_maproulette_metrics = maproulette_metrics.get_metrics:main",
            "get_user_ids = maproulette_metrics.get_user_ids:main",
            "set_maproulette_key = maproulette_metrics.set_api_key:main",
        ]
    },
)
