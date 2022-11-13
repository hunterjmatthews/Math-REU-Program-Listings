import requests
from bs4 import BeautifulSoup
import datetime
import pandas
import csv
import re

def website1():
    institute, location, subject_area, application_link, program_link, deadline, stipend, urls, newurls = [],[],[],[],[],[],[],[],[]
    base_url = "https://www.mathprograms.org/db?joblist-0-2---40-t--"
    base_page = requests.get(base_url)
    base = BeautifulSoup(base_page.content, "html.parser")  # Grab the entire html code from the site.
    for i in base.find_all('ol', {'class': 'sp5'}):
        links = i.find_all('a', href=True)
        for link in links:
            urls.append(link['href'])
    for s in urls:
        if '/db/program' in s:
            new_url = "https://www.mathprograms.org" + s
            ### Begin Middle Layer
            middle_page = requests.get(new_url)
            main = BeautifulSoup(middle_page.content, "html.parser")  # Grabs entire html code from the new link.
            ### Begin University/Institute
            university_element = main.find("h2")  # Finds h2 data.
            university_name = university_element.get_text()  # Grabs the name of the university.
            institute.append(university_name)  # Stores university/institute data in the 'institute' array.
            ### End University/Institute

            ### Begin Location
            location_element = main.find("b", text="Program Location:")  # Finds program location data.
            location_name = location_element.next_sibling.strip().replace('[',
                                                                          '')  # Grabs location data and cleans up the string.
            location.append(location_name)  # Stores location data in the 'location' array
            ### End Location

            ### Begin Subject Area
            find_subject_area = main.find("body")
            find_subject_area = find_subject_area.get_text()
            get_subject_area_index = find_subject_area.find("Subject Area:")
            get_application_deadline_index = find_subject_area.find("Application Deadline:")
            get_subject_area = find_subject_area[get_subject_area_index:get_application_deadline_index]
            get_subject_area = get_subject_area.replace('Subject Area:', '')
            get_subject_area = get_subject_area.strip()
            subject_area.append(get_subject_area)
            temp_hold = subject_area[:]
            for x in subject_area:
                if not x:
                    temp_hold[subject_area.index(x)] = 'Not Provided'
            subject_area = temp_hold[:]
            ### End Subject Area

            ### Begin Application Link
            apply_element = main.find(class_="btn")  # Finds the apply link from MathPrograms.
            apply_link = apply_element.get('href')  # Grabs the apply link from MathPrograms.
            application_link.append(apply_link)  # Stores link data in the 'apply' array.
            ### End Application Link

            ### Begin Program Link
            find_top_link = main.select("dd > a")
            if not find_top_link:
                find_top_link.append("Not Provided")
            for get_link in find_top_link:
                if get_link and get_link != "Not Provided":
                    top_link = get_link.text
                    program_link.append("[Program](" + top_link + ")")
                else:
                    program_link.append(get_link)
            ### End Program Link

            ### Begin Deadline
            get_application_deadline = main.find("b", text="Application Deadline:")
            get_application_deadline = get_application_deadline.next_sibling.strip()
            if "2023" in get_application_deadline:
                deadline.append(get_application_deadline)
            else:
                deadline.append("Not Provided")
        ### End Deadline
        ### End Middle Layer
        ### End Base Layer
    return institute, location, subject_area, application_link, program_link, deadline, stipend, urls, newurls


def website3():
    df = pandas.read_csv("https://docs.google.com/spreadsheets/d/1U-27BeHMSJCWumbNByal2tHyYo9wRVud9WoRE70E47Y/export?format=csv&gid=435769815")
    university_information = df['School/Institute'].tolist()
    location_information = df['Location'].tolist()
    start_date = df['Start date'].tolist()
    start_date = [str(i).replace('???', 'N/A') for i in start_date]
    end_date = df['End date'].tolist()
    end_date = [str(i).replace('???', 'N/A') for i in end_date]
    link = df['Link'].tolist()
    link = [re.sub(r'(https://www.mathprograms.org/db/programs/)\d\d\d\d', '', file) for file in link]
    return university_information, location_information, start_date, end_date, link


def get_rank(university_information, length):
    # Declarations:
    ranking_index, name_index = [None] * length, []
    # read csv, and split on "," the line
    csv_file = csv.reader(open('colleges.csv', "r"), delimiter=",")
    # loop through the csv list
    for row in csv_file:
        for name, value in enumerate(university_information):
        # if current rows 1st value is equal to input, insert that row.
            if value == row[1]:
                ranking_index.insert(int(name), row[0])
                name_index.append(name)
    return ranking_index, name_index

def create_readme(institute, location, subject_area, program_link, application_link, deadline,  university_information, location_information, start_date, end_date, link):
    # Create README.md file for GitHub.
    with open('README.md', 'w') as f:
        f.write("# 2023 Mathematics REU List")
        f.write("\n## Description: ")
        f.write("\nThis page contains a directory of 2023 Research Experience for Undergraduates (REUs) aimed at mathematics students.")
        f.write(" This directory is built automatically using a combination of Python, Github Actions, and data obtained from [MathPrograms](https://www.mathprograms.org) and [https://sites.google.com/view/mathreu](Math REU Programs).")
        f.write(" It is updated everyday at exactly 12:00 AM. In the future, I will update the program to pull from multiple REU sites.\n")
        f.write(" ## Math REU Programs: ")
        f.write("\n| University/Institute | Location | Subject Area | Program Link | Application Link | Deadline |")
        f.write("\n| -------------------- | -------- | ------------ | ------------ | ---------------- | -------- |")
        f.write("\n")
        # Loop to output all the data into the desired format.
        for x in range(0, len(institute)):
            f.write("| " + institute[x] + " | " + location[x] + " | " + subject_area[x] + " | " + program_link[x] + " | " + "[Apply](" + application_link[x] + ") | " + deadline[x] + " | \n")

        f.write("\n ## Math REU Programs: ")
        f.write("\n| University/Institute | Location | Start Date - End Date | Link |")
        f.write("\n| -------------------- | -------- | --------------------- | ---- |")
        f.write("\n")
        for x in range(0, len(university_information)):
            f.write("| " + university_information[x] + " | " + location_information[x] + " | " + start_date[x] + " - " + end_date[x] + " | " + link[x] + " |")
        # Generate the date and time the report was last generated.
        f.write('\nLast Update: %s.\n' % (datetime.datetime.now()))

    # Close File
    f.close()


if __name__ == "__main__":
    # Obtain university/institution name, location, start and end date, and link to the program.
    university_information, location_information, start_date, end_date, link = website3()
    # Obtain the length of the list.
    length = len(university_information)
    # Find the national ranking of the university (if applicable). Only working for U.S. institutions at the moment.
    rankings, university_index = get_rank(university_information, length)
    institute, location, subject_area, application_link, program_link, deadline, stipend, urls, newurls = website1()
    create_readme(institute, location, subject_area, program_link, application_link, deadline, university_information, location_information, start_date, end_date, link)
