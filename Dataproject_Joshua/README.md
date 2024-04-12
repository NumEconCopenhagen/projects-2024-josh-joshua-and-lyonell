# Data analysis project


Our project, titled **Exploring the Impact of Legal Drinking Age Changes**, focuses on constructing a dataset for applying a staggered Difference-in-Differences (DID) model. The objective of the DID analysis is to assess whether alterations in the legal drinking age affect employment rates. To achieve this, we exploit the heteroskedasticity in drinking age regulations across the United States from 1986 to 1988.
W focus on states that had one clear increase in drinking age form 19 to 21. The states Alabama, Florida and Minnesota experinced an increase in drinking age from 19 to 21 in 1986, Idaho in 1987 and Minnesota in 1988. The countries California, Indiana, Kentucky, Wyoming, Missouri, Nevada, New Mexico, North Dakota, Oregon, Pennsylvania, Utah had anconstant drinking age of 21 in the respective period.

The specific goal of our project is to generate a dataset that conforms to the requirements of the DID function in Stata, necessitating a long-format dataset. Additionally, we aim to derive initial insights from the dataset regarding potential implications for employment rates and assess the validity of the parallel trend assumption, a fundamental DID assumption.

The **results** of the project can be seen from running [dataproject.ipynb](dataproject.ipynb).

We apply the **following datasets**:

1. [CAINC4_ALL_AREAS_1969-2022.csv](https://apps.bea.gov/regional/downloadzip.cfm?_gl=1*pn7tgq*_ga*MTM0MTU4OTIzMS4xNzA5MjM4MDM1*_ga_J4698JNNFT*MTcwOTczOTQ2NC40LjEuMTcwOTc0MTM1MS4xMC4wLjA.)
2. [spi0404-3.csv](https://apps.bea.gov/regional/histdata/releases/0404spi/index.cfm)
3. [spi0404-5.csv](https://apps.bea.gov/regional/histdata/releases/0404spi/index.cfm)

**Dependencies:** Apart from a standard Anaconda Python 3 installation, the project requires the following installations:

``pip install matplotlib-venn``
