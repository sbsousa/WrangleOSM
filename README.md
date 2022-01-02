# WrangleOSM
OpenStreetMap Data Wrangling

Before data can be analyzed, it must be wrangled (collected, cleaned, and prepared). This project is an example of the wrangling process for an XML file that will be explored in a SQL database. The project was created for Udacity's Data Analyst Nanodegree.
 
Access the final report here: https://sbsousa.github.io/WrangleOSM

## Project Description:

Per Udacity, the goal of this project is to "choose any area of the world in https://www.openstreetmap.org and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap data for a part of the world that you care about. Choose to learn SQL or MongoDB and apply your chosen schema to the project."


## Approach

For this project, I analyzed OpenStreetMap data in the United States. The original data set is in XML format. I audited a small sample of the data and parsed the full XML file into multiple categorized CSV files using Python scripts. Then I imported it to a SQLite database to run additional queries.

The final analysis report is provided in a PDF.

## License:

This project is publicly available for educational purposes. Please acknowledge this source if you use it.

## Sources

The Python scripts and schema were provided by Udacity:

https://www.udacity.com/course/data-analyst-nanodegree--nd002

Udacity code that I modified is commented.

Additional sources are acknowledged in the code and report.