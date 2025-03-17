from setuptools import setup, find_packages

setup(
    name="solr_graph_playground",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pysolr>=3.9.0",
        "requests>=2.28.0",
        "python-dotenv>=0.20.0",
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'check-solr-collection=solr_graph_playground.solr_setup:check_collection',
            'create-solr-collection=solr_graph_playground.solr_setup:create_collection',
            'delete-solr-collection=solr_graph_playground.solr_setup:delete_collection',
            'recreate-solr-collection=solr_graph_playground.solr_setup:recreate_collection',
            'ingest-citations=solr_graph_playground.solr_setup:ingest_citations',
            'get-random-sample=solr_graph_playground.solr_setup:get_random_sample',
        ],
    },
    author="Scott Stults",
    description="A utility to build graph structures in Solr to experiment with the graph querying capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sstults/solr_graph_playground",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
