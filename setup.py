import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tuya2domoticz",
    version="0.0.6",
    author="Constantin Petra",
    author_email="constantin.petra@gmail.com",
    description="Tuya sensor subscription for Domoticz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/costa76/tuya2domoticz",
    project_urls={
        "Bug Tracker": "https://github.com/costa76/tuya2domoticz/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    package_data={'': ['conf/tuya2domoticz.initd', 'conf/tuya2domoticz.service']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'requests',
        'tuya-connector-python',
        'python-daemon'
    ]
)