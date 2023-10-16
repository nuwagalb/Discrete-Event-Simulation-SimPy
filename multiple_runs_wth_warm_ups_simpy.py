# Warm Up 
# A potential problem in our DES models is that, by default we
# assume that the system is empty of entities (e.g. patients) when
# the system starts.
# In some cases, that might be fine - for example, if we're simulating
# a day of Minor Injury Unit activity, where patients turn up from 
# when it opens and there's nobody left when it closes.
# But imagine we're modelling an ED or a hospital more generally. These
# systems are never empty, and so if we run our model starting from empty,
# then our results are going to be skewed by the fact that early on in the
# simulation, there were no or very few people in the model.
# Fortunately, there's a simple solution - we can use a warm up period
# During a warm up period, our model runs, but it doesn't collect any results.
# The warm-up period allows the simulation to get to a more representative
# state before we start collecting results
#
# 
#                                          Nurse
#      GENERATOR                ----------------      
#    People arriving      QUEUE | Weight Loss  |      
#    for weight loss ---------> | Consultation |-----------> SINK
#    consultation               |              |              
#                               ----------------              
#                                          Nurse
#      GENERATOR                ----------------      
#    People arriving      QUEUE | Perform test |      
#    for tests       ---------> | Consultation |-----------> SINK
#                               |              |              
#                               ----------------
#

import simpy
import random
from statistics import mean
import csv
import pandas as pd

# One arrivals generator function - for those coming for weight loss clinic
def patient_generator_weight_loss(env, wl_inter, mean_consult, nurse):
    while True:
        wp = activity_generator_weight_loss(env, mean_consult, nurse) 

        env.process(wp)

        t = random.expovariate(1.0/wl_inter)

        yield env.timeout(t)

# Another arrivals generator function - for those coming for tests
# This generator has a different inter-arrival time and uses different
# activity times
def patient_generator_test(env, t_inter, mean_test, nurse):
    while True:
        tp = activity_generator_test(env, mean_test, nurse)

        env.process(tp)

        t = random.expovariate(1.0/t_inter)

        yield env.timeout(t)

# Activity generator function for weight loss consultation
def activity_generator_weight_loss(env, mean_consult, nurse):
    global list_of_queuing_times_nurse
    global warm_up_period

    time_entered_queue_for_nurse_wl = env.now

    with nurse.request() as req:
        yield req

        time_left_queue_for_nurse_wl = env.now
        time_in_queue_for_nurse_wl = (time_left_queue_for_nurse_wl - 
                                   time_entered_queue_for_nurse_wl)

        # Now we only add this result to the list of results if the warm
        # up period has passed
        if env.now > warm_up_period:
            list_of_queuing_times_nurse.append(time_in_queue_for_nurse_wl)

        sampled_consultation_time = random.expovariate(1.0/mean_consult)

        yield env.timeout(sampled_consultation_time)

# Activity generator function for tests. Note - the resource we're requesting
# here is the same resource as for the other activity - the nurse
def activity_generator_test(env, mean_test, nurse):
    global list_of_queuing_times_nurse
    global warm_up_period

    time_entered_queue_for_nurse_t = env.now

    with nurse.request() as req:
        yield req

        time_left_queue_for_nurse_t = env.now
        time_in_queue_for_nurse_t = (time_left_queue_for_nurse_t - 
                                     time_entered_queue_for_nurse_t)
        
        # Now we only add this result to the list of results if the warm
        # up period has passed
        if env.now > warm_up_period:
            list_of_queuing_times_nurse.append(time_in_queue_for_nurse_t)

        sampled_test_time = random.expovariate(1.0 / mean_test)

        yield env.timeout(sampled_test_time)

# Set up number of times to run the simulation
number_of_simulation_runs = 100

# Specify the results collection and warm up period for each simulation run
results_collection_period = 120 # how long the simulation will run after warm up
warm_up_period = 120

# Create a file to store the results of each run, and write the column headers
with open("nurse_results.csv", "w") as f:
    writter = csv.writer(f, delimiter=",")

    writter.writerow(["Run", "Mean Q Nurse"])

# Run the simulation the number of times specified, storing the results of each
# run to file

for run in range(number_of_simulation_runs):
    # Set up the simulation environment
    env = simpy.Environment()

    # Set up the resources
    nurse = simpy.Resource(env, capacity=1)

    # Set up parameter values
    wl_inter = 8
    t_inter = 10
    mean_consult = 10
    mean_test = 3

    # Set up a list to store queuing times for the nurse
    list_of_queuing_times_nurse = []

    # Start the patients arrivals generators (we've got two to start this time)
    env.process(patient_generator_weight_loss(env, wl_inter, mean_consult, nurse))
    env.process(patient_generator_test(env, t_inter, mean_test, nurse))

    # Run the simulation
    env.run(until=(results_collection_period + warm_up_period))

    # Calculate and print mean queuing time for the nurse
    mean_queuing_time_nurse = mean(list_of_queuing_times_nurse)
    print(f"Mean queuing time for nurse (mins): {mean_queuing_time_nurse:.2f}")

    # Set up list to write to file - here we'll store the run number alongside
    # the mean queueing time for the nurse in that run
    list_to_write = [run, mean_queuing_time_nurse]

    # Store the run results to file. We need to open in append mode ('a').
    # otherwise we'll overwrite the file each time. That's why we set up the
    # new file before the for loop, to start a new for each batch of runs
    with open("nurse_results.csv", "a") as f:
        writter = csv.writer(f, delimiter=",")

        writter.writerow(list_to_write)

# After the batch of runs is complete, we might want to read the results back
# in and take some summary statistics
# Here, we're going to use a neat shortcut for easily reading a csv file into
# a pandas dataframe
results_df = pd.read_csv("nurse_results.csv")

# We now want to take the average queuing time across runs
mean_trial_queuing_time_nurse = results_df["Mean Q Nurse"].mean()
print(f"Mean queuing time over trial : {mean_trial_queuing_time_nurse:.2f}")

# Maybe the max and min run results too
max_trial_queuing_time_nurse = results_df["Mean Q Nurse"].max()
min_trial_queuing_time_nurse = results_df["Mean Q Nurse"].min()

print("Max mean queuing result over trial :",
      f"{max_trial_queuing_time_nurse:.2f}")
print("Min mean queuing result over trial :",
      f"{min_trial_queuing_time_nurse:.2f}")
# print(results_df)
      
