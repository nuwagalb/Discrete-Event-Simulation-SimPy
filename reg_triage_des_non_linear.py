# MORE THAN ONE SEQUENTIAL ACTIVITY - NON LINEAR
# Often in real world systems, not everything is linear. Different
# things might happen depending on certain conditions. For
# example, after triage a patient might be referred to a 
# Ambulatory Care to diagnose and treat the patient without
# being admitted to the hospital overnight.
#                                        Receptionist                Nurse
#      GENERATOR                ----------------              -----------
#    People arriving      QUEUE |              |      QUEUE   |         |
#    ED              ---------> | Registration |----------->  | Triage  |
#                               |              |              |         |
#                               ----------------              -----------
#                                                         20% /         \80%
#                                                            /           \
#                                                     QUEUE / ACU Doctor  \ QUEUE    ED Doctor
#                                                 -----------------   ------------------
#                                                 | Initial       |   |  Assessment in |
#                                                 | Assessment in |   |  ED            |
#                                                 | ACU           |   |                | 
#                                                 ------------------  -------------------

import simpy
import random

# Arrivals generator function
def patient_generator_ed(env, ed_inter, mean_register, mean_triage,
                         mean_ed_assess, mean_acu_assess,
                         receptionist, nurse, ed_doctor, acu_doctor):
    p_id = 0

    while True:
        # Create an instance of activity generator
        p = activity_generator_ed(env, mean_register, mean_triage, 
                                  mean_ed_assess, mean_acu_assess, 
                                  receptionist, nurse, ed_doctor, acu_doctor, p_id)
        
        # Run the activity generator
        env.process(p)

        # Sample time to next arrival
        t = random.expovariate(1.0/ed_inter)

        # Freeze until time elapsed
        yield env.timeout(t)

        p_id += 1

# Activity generator function
def activity_generator_ed(env, mean_register, mean_triage, mean_ed_assess,
                          mean_acu_assess, receptionist, nurse, ed_doctor,
                          acu_doctor, p_id):
    time_entered_queue_for_registration = env.now

    # Request a receptionist
    with receptionist.request() as req:
        # Freeze until the request can be met
        yield req

        time_left_queue_for_registration = env.now
        time_in_queue_for_registration = (time_left_queue_for_registration - 
                                          time_entered_queue_for_registration)
        print(f"Patient {p_id} queued for registration for",
              f"{time_in_queue_for_registration:.1f} minutes.")

        # Sample the time spent in registration
        sampled_registration_time = random.expovariate(1.0/mean_register)

        # Freeze until that time has elapsed
        yield env.timeout(sampled_registration_time)

    # Here, we're outside of the with statement, and so have just finished
    # with the receptionist. Which means we've started queuing for the nurse.
    # So we just do exactly as we did for the next activity in our system
    time_entered_queue_for_triage = env.now

    # Request for a nurse
    with nurse.request() as req:
        # Freeze until the request can be met
        yield req

        time_left_queue_for_triage = env.now
        time_in_queue_for_triage = (time_left_queue_for_triage - 
                                    time_entered_queue_for_triage)

        # Sample time spent in triage
        sampled_triage_time = random.expovariate(1.0/mean_triage)

        # Freeze until that time has elapsed
        yield env.timeout(sampled_triage_time)

    # We now encounter a branching path. Some patients will be sent to the
    # ACU, whilst others will remain in the ED. Here, we're just going to 
    # split them out using percentages probabilities, so let's randomly
    # sample from a uniform distribution to decide whether this patient stays
    # in ED or is referred to the ACU. Remember, a uniform distribution is
    # one in which there's an equal probability of any value being selected.
    # Therefore, we can randomly draw a number between 0 and 1, and compare 
    # that number against a threshold. If we want a 20% probability, then we
    # can see if the number sampled is lower than 0.2, because there was a
    # 20% chance of that happening (20% of the numbers that could have been chosen
    # between 0 and 1, with equal probability of any number being selected,
    # will fall less than 0.2)
    decide_acu_branch = random.uniform(0,1)

    # Then we can just use simple conditional logic to determine the next
    # activity for this patient. Here, we assume that 20% of patients will
    # sent to the ACU
    if decide_acu_branch < 0.2:
        # If the patient has gone down this path then they're now queuing for
        # an initial assessment in the ACU
        time_entered_queue_for_acu_assessment = env.now

        # Request an ACU doctor
        with acu_doctor.request() as req:
            # Freeze until the request can be met
            yield req

            time_left_queue_for_acu_assessment = env.now
            time_in_queue_for_acu_assessment = (
                time_left_queue_for_acu_assessment - 
                time_entered_queue_for_acu_assessment
            )
            print(f"Patient {p_id} queued for ACU assessment for",
                  f"{time_in_queue_for_acu_assessment:.1f} minutes")
            
            # Sample the time spent being assessed by the ACU doctor
            sampled_acu_assess_time = random.expovariate(1.0/mean_acu_assess)

            # Freeze until that time has elapsed
            yield env.timeout(sampled_acu_assess_time)
    else:
        # If the patient has gone down this path then they're now queuing for
        # an assessment from the ED doctore
        time_entered_queue_for_ed_assessment = env.now

        # Request an ED doctore
        with ed_doctor.request() as req:
            # Freeze until the request can be met
            yield req

            time_left_queue_for_ed_assessment = env.now
            time_in_queue_for_ed_assessment = (
                time_left_queue_for_ed_assessment - 
                time_entered_queue_for_ed_assessment
            )
            print(f"Patient {p_id} queued for ED assessment for",
                  f"{time_in_queue_for_ed_assessment:.1f} minutes")
            
            # Sample the time spent being assessed by the ED doctor
            sampled_ed_assess_time = random.expovariate(1.0 / mean_ed_assess)

            # Freeze until that time has elapsed
            yield env.timeout(sampled_ed_assess_time)

# Set up simulation environment
env = simpy.Environment()

# Set up resources
receptionist = simpy.Resource(env, capacity=1)
nurse = simpy.Resource(env, capacity=2)
ed_doctor = simpy.Resource(env, capacity=2)
acu_doctor = simpy.Resource(env, capacity=1)

# Set up parameter values
ed_inter = 8
mean_register = 2
mean_triage = 5
mean_ed_assess = 30
mean_acu_assess = 60

# Start the arrivals generator
env.process(patient_generator_ed(env, ed_inter, mean_register, mean_triage, 
                                 mean_ed_assess, mean_acu_assess,
                                 receptionist, nurse, ed_doctor, acu_doctor))

# Run the simulation
env.run(until=2880)




    