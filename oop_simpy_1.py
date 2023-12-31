#  -----------------------------     -------------------------    -----------------------
#  | CLASS: g                  |     | CLASS: Entity_1       |    | CLASS: Model        | 
#  |                           |     |                       |    |                     |
#  | Attributes                |     | Attributes            |    |  Attributes         | 
#  | global_parameter_A = 5    |     | entity_attribute_A    |    |  env                |
#  | global_parameter_B = 2    |     | entity_attribute_B    |    |  resource_1         |
#  | global_parameter_C = 72   |     | entity_attribute_C    |    |  resource_2         |
#  |                           |     |                       |    |                     |
#  | Methods                   |     | Methods               |    |  Methods            |
#  |                           |     | __init__              |    |  __init__           |
#  |                           |     |                       |    |  entity_generator   |
#  |                           |     |                       |    |  set_of_processes   |
#  |                           |     |                       |    |  run                |
#  -----------------------------     -------------------------    -----------------------
#
# We have a class that stores        We have a class for each      We have a class to represent
# global variable values that        of the entity types flowing   our model. The attributes of
# we'll need across the model        through our model. Each       this class will include the 
# (things like mean inter-arrival    entity may have attributes    simulation environment and any
# times, mean process times,         (e.g patient ID) and may      resources. Methods will include
# simulation duration, number of     have specific methods, or     the constructor, one or more 
# runs, etc). We don't create an     may just have a constructor   entity generators, one or more
# instance of this class - we just   Every time a new entity (e.g  functions describing sequences
# refer to the Class blueprint       patient) arrive, we create a  of events that will happen to
# itself                             new instance of this class    the entities, and a run function
#                                                                  that will start the entity
#                                                                  generators and run the model for
#                                                                  the required amount of time
#
# Example
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
#
#
#  CLASS STRUCTURE FOR THE ABOVE EXAMPLE
#  -----------------------------     -------------------------    ------------------------------
#  | CLASS: g                  |     | CLASS:                |    | CLASS:                     | 
#  |                           |     | Weight_Loss_Patient   |    | GP_Surgery_Model           |
#  | Attributes                |     |                       |    |                            | 
#  | wl_inter = 5              |     | Attributes            |    |  Attributes                |
#  | mean_consult = 6          |     | p_id: integer         |    |  env: simpy.Environment()  |
#  | number_of_nurses = 1      |     |                       |    |  nurse: simpy.Resource()   |
#  | sim_duration = 120        |     |                       |    |                            |
#  | number_of_runs = 10       |     | Methods               |    |  Methods                   |
#  |                           |     | __init__()            |    |  __init__()                |
#  | Methods                   |     |                       |    |  generate_wl_arrivals()    |
#  |                           |     |                       |    |  attend_wl_clinic(patient) |
#  |                           |     |                       |    |  run()                     |
#  -----------------------------     -------------------------    ------------------------------
#
#

import simpy
import random

# Class to store global parameter values.  We don't create an instance of this
# class - we just refer to the class blueprint itself to access the numbers
# inside.  Therefore, we don't need to specify a constructor.
class g:
    wl_inter = 5
    mean_consult = 6
    number_of_nurses = 1
    sim_duration = 120
    number_of_runs = 1
    
# Class representing our patients coming in for the weight loss clinic.
# Here, we only have a constructor method, that sets up the patient's ID
class Weight_Loss_Patient:
    def __init__(self, p_id):
        self.id = p_id
        
# Class representing our model of the GP Surgery.
class GP_Surgery_Model:
    # Here, the constructor sets up the SimPy environment, sets a patient
    # counter to 0 (which we'll use for assigning patient IDs), and sets up
    # our resources (here just a nurse resource, with capacity given by
    # the number stored in the g class)
    def __init__(self):
        self.env = simpy.Environment()
        self.patient_counter = 0
        
        self.nurse = simpy.Resource(self.env, capacity=g.number_of_nurses)
        
    # A method that generates patients arriving for the weight loss clinic
    def generate_wl_arrivals(self):
        # Keep generating indefinitely (until the simulation ends)
        while True:
            # Increment the patient counter by 1
            self.patient_counter += 1
            
            # Create a new patient - an instance of the Weight_Loss_Patient 
            # class, and give the patient an ID determined by the patient
            # counter
            wp = Weight_Loss_Patient(self.patient_counter)
            
            # Get the SimPy environment to run the attend_wl_clinic method
            # with this patient (remember, the environment is now stored
            # against the model class that we're in here, so we need to use
            # self. to refer to the environment)
            self.env.process(self.attend_wl_clinic(wp))
            
            # Randomly sample the time to the next patient arriving for the
            # weight loss clinic.  The mean is stored in the g class.
            sampled_interarrival = random.expovariate(1.0 / g.wl_inter)
            
            # Freeze this function until that time has elapsed
            yield self.env.timeout(sampled_interarrival)
            
    # A method that models the processes for attending the weight loss clinic.
    # The method needs to be passed a patient who will go through these
    # processes
    def attend_wl_clinic(self, patient):
        # Print the time the patient started queuing for a nurse
        print (f"Patient {patient.id} started queuing at {self.env.now:.1f}")
        
        # Request a nurse (remember, the nurse is now stored against the model
        # class that we're in here, so we need to use self. to refer to the
        # nurse resource)
        with self.nurse.request() as req:
            # Freeze the function until the request for a nurse can be met
            yield req
            
            # Print the time the patient finished queuing for a nurse
            print (f"Patient {patient.id} finished queuing at",
                   f"{self.env.now:.1f}")
            
            # Randomly sample the time the patient will spend in consultation
            # with the nurse.  The mean is stored in the g class.
            sampled_cons_duration = random.expovariate(1.0 / g.mean_consult)
            
            # Freeze this function until that time has elapsed
            yield self.env.timeout(sampled_cons_duration)
    
    # The run method starts up the entity generator(s), and tells SimPy to
    # start running the environment for the duration specified in the g class.
    def run(self):
        self.env.process(self.generate_wl_arrivals())
        
        self.env.run(until=g.sim_duration)

# Everything above is a definition of classes and functions, but here's where
# the code will start actively doing things.        
# For the number of runs specified in the g class, create an instance of the
# GP_Surgery_Model class, and call its run method
for run in range(g.number_of_runs):
    print (f"Run {run+1} of {g.number_of_runs}")
    my_gp_model = GP_Surgery_Model()
    my_gp_model.run()
    print ()