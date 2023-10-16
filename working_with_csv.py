# define a function
# read patient data file
# store four different fields in four different different lists
# calculate no of patient records read in
# print message to user showing no of records read in
# calculate average age of patients
# print message of average age to 2dp
# calculate no of patients that live in each of three counties
# display these results
# calculate % split for vaccinated vs unvaccinated
# display these results to user
# write results of 2-5 above to file called results.csv; first row
# indicating name(column header) of results (Number of records, Average age
# Number in Cornwall, etc), and the second row results themselves

import csv

list_of_names = []
list_of_vac_status = []
list_of_age = []
list_of_counties = []

with open("input_data.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")

    for line in reader:
        list_of_names.append(line[0])
        list_of_vac_status.append(line[1])
        list_of_age.append(int(line[2]))
        list_of_counties.append(line[3])

    print(f"list of names: {list_of_names}")
    print(f"list of vaccination status: {list_of_vac_status}")
    print(f"list of ages: {list_of_age}")
    print(f"list of counties: {list_of_counties}")

# no of patient records read in
if list_of_names:
    total_records = 0
    for record in list_of_names:
        total_records += 1
else:
    total_records = 0
print(f"Total Records that have been read: {total_records}")

# average age for patients
# first find total age in list of ages
age_total = sum(list_of_age)

average_age = round(age_total/total_records, 2)
print(f"Average age of patients is: {average_age}")

patients_in_cornwall = [
    county for county in list_of_counties if county == "Cornwall"]
patients_in_devon = [
    county for county in list_of_counties if county == "Devon"]
patients_in_somerset = [
    county for county in list_of_counties if county == "Somerset"]

if patients_in_cornwall:
    total_cornwall_patients = 0
    for patient in patients_in_cornwall:
        total_cornwall_patients += 1
else:
    total_cornwall_patients = 0

if patients_in_devon:
    total_devon_patients = 0
    for patient in patients_in_devon:
        total_devon_patients += 1
else:
    total_devon_patients = 0

if patients_in_somerset:
    total_somerset_patients = 0
    for patient in patients_in_somerset:
        total_somerset_patients += 1
else:
    total_somerset_patients = 0


vaccinated_patients = [
    vac_pat for vac_pat in list_of_vac_status if vac_pat == "Yes"]
unvaccinated_patients = [
    unvac_pat for unvac_pat in list_of_vac_status if unvac_pat == "No"]

if vaccinated_patients:
    total_vaccinated_patients = 0
    for patient in vaccinated_patients:
        total_vaccinated_patients += 1
    total_vaccinated_patients_perc = (
        total_vaccinated_patients/total_records) * 100
else:
    total_vaccinated_patients_perc = (0/total_records) * 100

if unvaccinated_patients:
    total_unvaccinated_patients = 0
    for patient in unvaccinated_patients:
        total_unvaccinated_patients += 1
    total_unvaccinated_patients_perc = (
        total_unvaccinated_patients/total_records) * 100
else:
    total_unvaccinated_patients_perc = (0/total_records) * 100

list_of_results_names = [
    'Number of Records',
    'Average age',
    'Number in Cornwall',
    'Number in Devon',
    'Number in Somerset',
    'Percentage of Vaccinated',
    'Percentage of Unvaccinated']

list_of_results = [
    total_records,
    average_age,
    total_cornwall_patients,
    total_devon_patients,
    total_somerset_patients,
    total_vaccinated_patients_perc,
    total_unvaccinated_patients_perc
]

lists_to_write = [list_of_results_names, list_of_results]

with open("results.csv", "w") as f:
    writter = csv.writer(f, delimiter=",")

    for sublist in lists_to_write:
        writter.writerow(sublist)
