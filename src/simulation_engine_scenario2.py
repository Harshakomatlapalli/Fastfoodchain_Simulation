import simpy 
import random
import pandas as pd
import numpy as np

# Load the CSV
df = pd.read_csv('../data/arrival_rates.csv')

# Convert the arrival rate column into a numpy array so the class can use it
arrival_rates = df["Customer_Arrival_Rate"].to_numpy()

class FastFoodChain_scenario2:
    def __init__(self, env, arrival_rate):
        self.env = env
        self.arrival_rate = arrival_rate
        self.associate = simpy.Resource(env, capacity=1)
        self.order_fullfillment = simpy.Resource(env, capacity=2) 
        self.cook = simpy.Resource(env, capacity=3) 
        self.stats = []
        self.util_log = []
    
    def monitor_resources(self):
        while True:
            self.util_log.append({
                "Time" : self.env.now,
                "Front_counter_Associate" : self.associate.count,
                "Cook" : self.cook.count,
                "Order_fullfillment_Associate" : self.order_fullfillment.count,
                "Production_Wait_Queue": len(self.cook.queue),
                "Order_Fullfillment_Associate_queue" :len(self.order_fullfillment.queue),
                "Front_Counter_Associate_queue" : len(self.associate.queue)
            })
            yield self.env.timeout(0.05)

    def arrivalrate(self):
        i = 0
        while True:
            hour_index = int(self.env.now / 60)
            if hour_index >= len(self.arrival_rate):
                print("Simulation complete")
                break
            lambd = self.arrival_rate[hour_index] / 60 # Converted to minutes
            yield self.env.timeout(random.expovariate(lambd))
            order_time = self.env.now
            i += 1
            customer_id = f"Customer:{i:03d}"
            customer_record = {
                "Time" : self.env.now,
                "Customer_Id" : customer_id,
                "Customer_Arrived" : order_time,
                "Ordered_time" : None,
                "Production_time" : None,
                "order_fullfillment" : None,
                "Hand-off/Exit" : None,
                "Left_with_out_ordering" : 0
            }
            self.stats.append(customer_record)

            if len(self.cook.queue)> 20:
                customer_record["Left_with_out_ordering"] = 1
                continue

            self.env.process(self.order(customer_id, customer_record))
            
    def order(self, customer_id, customer_record):
        if random.random() < 0.25: # at front counter
            with self.associate.request() as associate_req:
                yield associate_req
                yield self.env.timeout(random.triangular(1, 2, 1.5)) 
                customer_record["Ordered_time"] = self.env.now
                print(f"{customer_id} ordered (Counter) at {self.env.now:.2f}")
        else: #online & Kiosks (In store  & drive through)
                yield self.env.timeout(0.5) 
                customer_record["Ordered_time"] = self.env.now
                print(f"{customer_id} ordered (Kiosk) at {self.env.now:.2f}")
    
        self.env.process(self.kitchen_production(customer_id, customer_record))

    def kitchen_production(self, customer_id, customer_record):
        cook_req = self.cook.request()
        associate_req = self.associate.request()

        if len(self.associate.queue) <= 15:
                result = yield cook_req | associate_req
                
                if cook_req in result:
                    current_resource, current_request = self.cook, cook_req
                    if associate_req in result:
                        self.associate.release(associate_req)
                    else:
                        associate_req.cancel()
                else:
                    current_resource, current_request = self.associate, associate_req
                    if cook_req in result:
                        self.cook.release(cook_req)
                    else:
                        cook_req.cancel()
        else:
            yield cook_req
            current_resource, current_request = self.cook, cook_req
        
        yield self.env.timeout(random.triangular(1.5, 3, 2)) #Upgrade to kitchen may be more fryers or grill space

        customer_record["Production_time"] = self.env.now
        print(f"For {customer_id} production done at {self.env.now:.2f}")

        #Release request
        current_resource.release(current_request)

        self.env.process(self.packing(customer_id, customer_record))

    #Assembling burgers and packing
    def packing(self, customer_id, customer_record):
        with  self.order_fullfillment.request() as packing_req:
                yield packing_req
                yield self.env.timeout(random.triangular(1,1.5,1.5)) #Automated labelling
                customer_record["order_fullfillment"] = self.env.now
                print(f"For {customer_id} order_fullfilled at {self.env.now:.2f}")
        self.env.process(self.dinein(customer_id, customer_record))

    def dinein(self, customer_id, customer_record):
        if random.random() < 0.60:
            # Grab and go
            customer_record["Hand-off/Exit"] = self.env.now
            print(f"For {customer_id} exit (Takeaway) at {self.env.now:.2f}")
            return
        else:
            # Eat in
            yield self.env.timeout(random.triangular(25, 30, 40)) 
            customer_record["Hand-off/Exit"] = self.env.now
            print(f"For {customer_id} exit (Dine-in) at {self.env.now:.2f}")

random.seed(46)
# Setup and Run
env = simpy.Environment()
obj2 = FastFoodChain_scenario2(env, arrival_rate)
env.process(obj2.arrivalrate())
env.process(obj2.monitor_resources())
env.run(until=1200) # Run for 20 hours 

