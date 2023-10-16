# MULTIPLE GENERATORS
# It's easy to capture multiple entry points into our system in SimPy
# - we just set up more than one entity generator!
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

    time_entered_queue_for_nurse_wl = env.now

    with nurse.request() as req:
        yield req

        time_left_queue_for_nurse_wl = env.now
        time_in_queue_for_nurse_wl = (time_left_queue_for_nurse_wl - 
                                   time_entered_queue_for_nurse_wl)

        # Append the calculated time in queue for this patient to our
        # global list of queuing times for all patients
        list_of_queuing_times_nurse.append(time_in_queue_for_nurse_wl)

        sampled_consultation_time = random.expovariate(1.0/mean_consult)

        yield env.timeout(sampled_consultation_time)

# Activity generator function for tests. Note - the resource we're requesting
# here is the same resource as for the other activity - the nurse
def activity_generator_test(env, mean_test, nurse):
    global list_of_queuing_times_nurse

    time_entered_queue_for_nurse_t = env.now

    with nurse.request() as req:
        yield req

        time_left_queue_for_nurse_t = env.now
        time_in_queue_for_nurse_t = (time_left_queue_for_nurse_t - 
                                     time_entered_queue_for_nurse_t)
        list_of_queuing_times_nurse.append(time_entered_queue_for_nurse_t)

        sampled_test_time = random.expovariate(1.0 / mean_test)

        yield env.timeout(sampled_test_time)

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
env.run(until=120)

# Calculate and print mean queuing time for the nurse
mean_queue_time_nurse = mean(list_of_queuing_times_nurse)
print(f"Mean queuing time for nurse (mins): {mean_queue_time_nurse:.2f}")