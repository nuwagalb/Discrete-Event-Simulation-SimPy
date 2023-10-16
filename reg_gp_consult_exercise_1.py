# Exercise 1: Build a DES model in SimPy, of the below system. Run for 8 hours of simulated time
# Add functionality to the model to calculate and print the mean queuing times for each of the
# three queues, along with the mean time in system (from point of arrival to the surgery, to point
# of departure). For extra points, additionally plot a bar chart showing these times.
#
# You have 1 hour (+ 5 minutes comfort break). Work in your groups
#
#
#                                        Receptionist                       GP
#      GENERATOR                ----------------              -------------------
#    People arriving      QUEUE |              |      QUEUE   | GP Consultation |    75%
#    at GP surgery   ---------> | Registration |----------->  | 8 mins (mean)   |--------> SINK
#    Every 3 minutes            | 2 mins (mean)|              |                 |
#    (mean)                     ----------------              -------------------
#                                                                      |
#                                   Receptionist                       | 25%
#                      -----------------                               |
#             -------> | Answering call|--------> SINK         QUEUE   | Receptionist
#    Every 10 minutes  | 4 mins(mean)  |                               ⌄        
#    (mean)            -----------------                      --------------------
#                                                             | Book Test        |
#                                                             | 4 mins(mean)     |-------> SINK
#       There is 1 receptionist and 2 GPs                     |                  |
#                                                             --------------------
# Exercise 2
# Extend the DES model you built in Exercise 1 to include:
# - calls coming in to reception on average every 10 minutes, and which last an average of 4 minutes,
# answered by the receptionist. Don't worry about adding any results for call queues, or adding these
# calls to times in systems results. We just want to model the drain on the receptionist resource for
# other activities (registering patients and booking tests)
# - a warm up period of 3 hours before the 8 hours results collection period
# - functionality to run the simulation multiple times - have the simulation run 100 times, with average
# results taken over these runs
# 
# You have been asked by the GP surgery staff to use your model to make recommendations
# for resourcing to try to get the average time a person spends in the surgery to no more than
# around 30 minutes. What recommendations would you make? You have 40 minutes. We'll share the 
# solution at the end of this session
# 
# ANSWER
# After modeling the system, we discover that adding one extra receptionist and one extra 
# gp would significantly reduce the time a patient spends in the surgery

# Exercise 1 Approach
# INPUTS (simulation time = 8 x 60 = 480 mins, mean_arrival_time = 3 mins, mean registration time = 2 mins, 
# mean consultation time = 8 mins, mean booking test time = 4 mins, percentage of those who book test = 25%,
# percentage who leave system without booking test = 75%, Resources: 1 receptionist, 2 gps)
# OUTPUTS (mean queing time for registration queue, mean queing time for consultation queue, mean
# queuing time for book test queue, mean time in the system (point of arrival to point of departure), plot bar for these times)

# Exercise 2 Approach
# INPUTS (c_inter = 10 min, mean_call_time = 4 min, receptionist, warm_up_period = 3x60 mins, simulation_run_times=100, consider
# average results for these runs), model drain on the recepionist resource



import simpy
import random
from statistics import mean
import csv
import pandas as pd

# Create Patient Arrivals Generator
def patient_generator_gp(env, gp_inter, mean_register, mean_consult,
                        mean_book_test, receptionist, gps):
    # do this indefinitely
    while True:
        # create an instance of the activity generator for the person's journey in the GP's office
        p = activity_generator_gp(env, mean_register, mean_consult,
                                  mean_book_test, receptionist, gps)
        
        # run the activity generator
        env.process(p)

        # sample the arrival time for the next person from an exponential distribution
        t = random.expovariate(1.0 / gp_inter)

        # Freeze this function until this sampled time has elapsed
        yield env.timeout(t)

# Create Telephone Calls Arrivals Generator
def call_generator_reception(env, call_inter, mean_call, receptionist):
    while True:
        # Create an instance of the activity generator
        c = activity_generator_call(env, mean_call, receptionist)
        
        # Run the activity generator
        env.process(c)

        # Sample the arrival time for the next call from an exponential distribution
        t = random.expovariate(1.0 / call_inter)

        # Freeze this function until this sampled time has elapsed
        yield env.timeout(t)

# Activity generator for receptionist taking telephone calls
def activity_generator_call(env, mean_call, receptionist):
    with receptionist.request() as req:
        yield req

        sampled_call_time = random.expovariate(1.0 / mean_call)

        yield env.timeout(sampled_call_time)
        
# Activity generator for receptionist registering patients
def activity_generator_gp(env, mean_register, mean_consult, mean_book_test,
                          receptionist, gps):
    # Define the global lists we will be using to capture mean times and system
    # times
    global list_of_times_spent_in_registration_queue
    global list_of_times_spent_in_gp_consultation_queue
    global list_of_times_spent_in_booking_test_queue
    global list_of_times_spent_in_the_entire_system
    global warm_up_period

    # Record entrance of person within the system
    time_entered_system = env.now

    # person enters queue for registration
    time_entered_queue_for_registration = env.now

    # Request for a receptionist
    with receptionist.request() as req:
        # Freeze the function until a receptionist is present to register a patient
        yield req

        # Once the receptionist becomes available, leave the queue
        time_left_queue_for_registration = env.now

        # Calculate the time spent in the registration queue
        time_spent_in_registration_queue = (
            time_left_queue_for_registration - 
            time_entered_queue_for_registration
        )

        # Append the time spent by person in queue to our global list
        if env.now > warm_up_period:
            list_of_times_spent_in_registration_queue.append(
                time_spent_in_registration_queue
            )

        # Calculate how long it takes for the person to be registered
        time_spent_for_registration = random.expovariate(1.0 / mean_register)

        # Freeze the function until the registration process is done
        yield env.timeout(time_spent_for_registration)
    
    # At this point, the person is done with registration and enters the
    # GP consultation queue
    time_entered_queue_for_gp_consultation = env.now

    # we then request for a gp to cater to the person
    with gps.request() as req:
        # Freeze until one of the gps is available
        yield req

        # When the gp is available, we can now leave the gp consultation
        # queue
        time_left_queue_for_gp_consultation = env.now
        time_spent_in_gp_consultation_queue = (
            time_left_queue_for_gp_consultation - 
            time_entered_queue_for_gp_consultation
        )

        # append time spent by person in consultation queue to our global list
        if env.now > warm_up_period:
            list_of_times_spent_in_gp_consultation_queue.append(
                time_spent_in_gp_consultation_queue
            )

        # Calculate how long the gp consultation process takes using an
        # exponential distribution
        time_spent_for_consultation = random.expovariate(1.0 / mean_consult)

        # Freeze until the consultation process is done
        yield env.timeout(time_spent_for_consultation)

    # At this point, the person is done with consulting with the GP, which
    # leaves him with a 75% chance of leaving the office or a 25% chance of
    # being sent back to the receptionist to book a test
    # Let us calculate the probability of the patient having a 75% chance of
    # leaving and a 25% chance of staying. We will pick a random number between
    # 0 and 1 from a uniform distribution and if the number is less than 0.25,
    # then this represents a 25% chance for the patient to be sent back to the
    # receptionist to book a test, however, if the number is greater than 25%,
    # then this follows within the 75% range so it is a chance that the 
    # person will leave the GP's office needing no other service
    decide_test_needed = random.uniform(0,1)

    # If the booking_test_chance number is greater than 0.25%, patient exits
    # the office
    if decide_test_needed < 0.25:
        # Enter the booking test queue
        time_entered_queue_for_booking_test = env.now

        # Request for a receptionist
        with receptionist.request() as req:
            # Freeze until a receptionist is available
            yield req

            # Once the receptionist becomes available, leave the booking test
            # queue
            time_left_queue_for_booking_test = env.now
            time_spent_in_booking_test_queue = (
                time_left_queue_for_booking_test - 
                time_entered_queue_for_booking_test
            )

            # append the time spent by person in booking test queue to our global
            # list
            if env.now > warm_up_period:
                list_of_times_spent_in_booking_test_queue.append(
                    time_spent_in_booking_test_queue
                )

            # we now exponential sample how long it takes for the booking test
            # process
            time_spent_for_booking_test = random.expovariate(1.0 / mean_book_test)

            # Freeze until the sampling process for booking a test is done
            yield env.timeout(time_spent_for_booking_test)

    # At this point, the person has been fully processed and is ready to exit
    # the entire system. So record this time
    time_exited_system = env.now    

    # Find the total time spent within the system
    time_spent_in_system = (
        time_exited_system - 
        time_entered_system
    )

    # Append this system time to our global list_of_times_spent_in_entire_system list
    if env.now > warm_up_period:
        list_of_times_spent_in_the_entire_system.append(time_spent_in_system)

# Both the arrival and activity generator are created at this point, 
# let us go ahead and use them
# Set up number of times to run the simulation
number_of_simulation_runs = 100

# Specify the results collection and warm up period for each simulation run
results_collection_period = 480 # how long the simulation will run after warm up
warm_up_period = 180

# Create a file to store the results of each run, and write the column headers
with open("gp_results.csv", "w") as f:
    writter = csv.writer(f, delimiter=",")

    writter.writerow(["Run", "Mean Q Registration", "Mean Q Consultation", 
                      "Mean Q Booking Test", "Mean System Time"])

# Run the simulation the number of times specified, storing the results of each
# run to file

for run in range(number_of_simulation_runs):
    # Create a simulation environment
    env = simpy.Environment()

    # Create our resources
    receptionist = simpy.Resource(env, capacity=2) # base case = 1
    gps = simpy.Resource(env, capacity=3) # base case = 2

    # Create lists to hold means for the different queues
    # mean time in the system (point of arrival to point of departure)
    list_of_times_spent_in_registration_queue = []
    list_of_times_spent_in_gp_consultation_queue = []
    list_of_times_spent_in_booking_test_queue = []
    list_of_times_spent_in_the_entire_system = []

    # Enter parameters here
    gp_inter = 3
    call_inter = 10
    mean_register = 2
    mean_consult = 8
    mean_book_test = 4
    mean_call = 4

    # Start the arrivals generator (in-person and incoming calls)
    env.process(patient_generator_gp(env, gp_inter, mean_register,
                                     mean_consult, mean_book_test,
                                     receptionist, gps))
    env.process(call_generator_reception(env, call_inter, mean_call,
                                         receptionist))

    # Run the simulation for 8 hours
    env.run(until=(warm_up_period + results_collection_period )) 

    # Print the different mean queuing times for registration, consultation,
    # booking, and mean time spent in entire system
    mean_queuing_time_for_registration = mean(list_of_times_spent_in_registration_queue)
    mean_queuing_time_for_gp_consultation = mean(list_of_times_spent_in_gp_consultation_queue)
    mean_queuing_time_for_booking_test = mean(list_of_times_spent_in_booking_test_queue)
    mean_time_spent_in_entire_system = mean(list_of_times_spent_in_the_entire_system)

    # Set up list to write to file - here we'll store the run number alongside
    # all the other mean values in that run
    list_to_write = [run,
                     mean_queuing_time_for_registration,
                     mean_queuing_time_for_gp_consultation,
                     mean_queuing_time_for_booking_test,
                     mean_time_spent_in_entire_system]

    # Store the run results to file. We need to open in append mode ('a').
    # otherwise we'll overwrite the file each time. That's why we set up the
    # new file before the for loop, to start a new for each batch of runs
    with open("gp_results.csv", "a") as f:
        writter = csv.writer(f, delimiter=",")

        writter.writerow(list_to_write)

# After the batch of runs is complete, we might want to read the results back
# in and take some summary statistics
# Here, we're going to use a neat shortcut for easily reading a csv file into
# a pandas dataframe
results_df = pd.read_csv("gp_results.csv")

# We now want to take the average queuing time across runs
mean_trial_queuing_time_for_registration = results_df["Mean Q Registration"].mean()
mean_trial_queuing_time_for_consultation = results_df["Mean Q Consultation"].mean()
mean_trial_queuing_time_for_booking_test = results_df["Mean Q Booking Test"].mean()
mean_trial_overall_system_time = results_df["Mean System Time"].mean()

print("Trial Results")
print("---------------------------------------------------")
print(f"Mean registration queuing time (mins) : {mean_trial_queuing_time_for_registration:.2f}")
print(f"Mean consultation queuing time (mins) : {mean_trial_queuing_time_for_consultation:.2f}")
print(f"Mean booking test queuing time (mins) : {mean_trial_queuing_time_for_booking_test:.2f}")
print(f"Mean overall system time over (mins) : {mean_trial_overall_system_time:.2f}")
