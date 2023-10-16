# --------------------------------
# | Inter-Arrival Times:         |
# | - Arrivals waiting for       |
# |   weight loss consultation   |                                           Nurse
# |                              |      GENERATOR                  ----------------
# | Entities                     |      People arriving      QUEUE | Weight Loss  |
# | - WL Clinic Patients         |      for wait loss   ---------> | Consultation |--------> SINK
# |                              |      consultation               |              |
# | Activity Times:              |                                 ----------------
# | - Time spent in weight loss  |
# |   consultation               |
# |                              |
# --------------------------------

# Pseudo Code: Import simpy and random libraries
import simpy
import random

# Generator function for our patient generator (that will bring new patients
# into the model). We pass into the function the simulation environment along
# with any parameter values and resources we'll need to use or pass on here.
# In this example, we pass in mean inter-arrival time for patients coming in,
# the mean time patients spend in a consultation and the nurse resource
#Pseudo Code: Patient Arrivals generator function
def patient_generator_weight_loss(env, wl_inter, mean_consult, nurse):
    p_id = 0 # We'll set this up to give each patient created a unique ID

    # Keep doing this indefinitely (whilst the program's running)
    # Pseudo Code: Keep generating Patients indefinitely
    while True:
        # Create an instance of the activity generator function (defined
        # below) which will define what happens to our patients. Give the
        # generator function the inputs it needs - in this case, the 
        # simulation environment, the mean consultation time, the nurse
        # resource, and the patient ID. We don't need to pass accross the
        # inter-arrival time as it's only needed here in the arrivals
        # generator
        # Pseudo Code: Create an instance of the patient's activity generator
        wp = activity_generator_weight_loss(env, mean_consult, nurse, p_id)

        # Tell the simulation environment to run the activity generator
        # function for this instance of the generator function (essentially
        # representing a single patient and its journey here)
        # Pseudo Code: run the activity generator for this patient
        env.process(wp)

        # Calculate the time (in minutes) until the next patient arrives - here we sample
        # from an exponential distribution with the mean we passed in
        #Pseudo code: Sample the time until next patient
        t = random.expovariate(1.0/wl_inter)

        # Tell the simulation to freeze this function in place until that
        # sampled inter-arrival time has elapsed
        #Pseudo code: Freeze generation of patients until that time has passed
        yield env.timeout(t)

        # When the time has elapsed, and we're ready for the next patient to
        # arrive, this generator function will resume from here. So the first
        # thing it will do is increment the patient ID by 1 ready to be used
        # for the next patient
        #Pseudo code: Proceed to generate new patient
        p_id += 1

# Generator function for the activities that our entities (patients here) will
# queue for. Think of this as the function that describes the patient's 
# journey through the system. It needs to be passed the environment, along
# with any parameter values and resources it needs - here, the mean
# consultation time, the nurse resource and the patient ID
# Pseudo Code: Patient activity generator function with parameters 
def activity_generator_weight_loss(env, mean_consult, nurse, p_id):
    # We can use the 'now' attribute of the simulation environment to grab
    # the current simulation time, which is useful for recording when a 
    # patient joined a queue for example. Here, we also print it out for the 
    # user.
    time_entered_queue_for_nurse = env.now
    print (f"Patient {p_id} joined queue @ {time_entered_queue_for_nurse:.1f}")

    # We now call the request() function of the Nurse resource, and we use a
    # 'with' statement to indicate that all of the code in the indented block
    # needs to be done with the nurse resource, after which it can release it
    # (like we saw with using 'with' for keeping a file open whilst we needed
    # it).
    # Pseudo code: request for a nurse
    with nurse.request() as req:
        # The first thing we do with the request is call a yield on it. This
        # means the function freezes in place until the request can be met 
        # (i.e there's a nurse available for the request to be met)
        # Pseudo code; Freeze until the request can be met
        yield req

        # Once the function unfreezes, it'll resume from here, so when we get
        # to this point we know a nurse is now available, and the patient has 
        # finished queuing. So we can record the current simulation time, and
        # therefore work out how long the patient was queuing
        # Pseudo code: Calculate the time the patient was queuing
        time_left_queue_for_nurse = env.now
        print(f"Patient {p_id} left queue @ {time_left_queue_for_nurse:.1f}")
        time_in_queue_for_nurse = (time_left_queue_for_nurse - 
                                   time_entered_queue_for_nurse)
        print(f"Patient {p_id} queued for {time_in_queue_for_nurse:.1f} mins")

        # Now the patient is with the nurse, we need to calculate how long
        # they spend in their consultation. Here, we'll randomly sample
        # from an exponential distribution with the mean we passed into the
        # function.
        #Pseudo code: Sample time spent with the nurse
        sampled_consultation_time = random.expovariate(1.0/mean_consult)

        # Tell the simulation to freeze this function in place until that
        # sampled consultation time has elapsed (which is also keeping the
        # nurse in use and unavailable elsewhere, as we're still in the 'with'
        # statement)
        #Pseudo code: Freeze until that time has passed
        yield env.timeout(sampled_consultation_time)

        # Once we get here, then control has been passed back to this instance
        # of the generator function, as so we know that the activity time we 
        # sampled above has now elapsed.
        # Let's print when the patient leaves the consultation
        print(f"***Patient {p_id} finished at {env.now:.1f}")

# We defined the generator functions above. Here's where we'll get everything
# running (remember - they've only been defined so far, not used)
# First we set up a new Simpy simulation environment. This is the environment
# that will hold our model
# Pseudo code: set up the simulation environment
env = simpy.Environment()

# Then we'll create a new SimPy resource called "nurse". We give it the 
# simulation environment in which it will live, and the capacity (number of
# nurses available). This allows us to change resource availablilty really
# easily.
# Pseudo code: set up the resources
nurse = simpy.Resource(env, capacity=1)

# We'll set our model parameter values here. In this case, the mean
# inter-arrival time for patients coming in for the weight loss clinic, and 
# the mean time patients will spend in a consultation. Remember - we're going
# to sample randomly for each patient from distributions with these means.
# We would also expect queues to start forming here, as people are, on
# average, arriving about a minute quicker than the nurse, on average, gets
# through a consultation.
# Pseudo code: set up parameter values
wl_inter = 5
mean_consult = 6

# Start up our patient generator function so we start creating patients
# Pseudo code: start the patients arrivals generator
env.process(patient_generator_weight_loss(env, wl_inter, mean_consult, nurse))

# Set the simulation to run for 120 time units (representing minutes in our
# model, so for 2 hours of simulated time)
# Pseudo code: run the simulation
env.run(until=120)
