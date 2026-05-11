import simpy 
import random

class FastFoodchain:
    def __init__(self, env, arrival_rate):
        self.env = env
        self.arrival_rate = arrival_rate
        self.associate = simpy.Resource(env, capacity=1.5)
        self.order_fullfillment = simpy.Resource(env, capacity=1.5)
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

            if len(self.associate.queue) > 10:
                customer_record["Left_with_out_ordering"] = 1
                continue

            self.env.process(self.order(customer_id, customer_record))
            
    def order(self, customer_id, customer_record):
        if random.random() < 0.70: #Drive through & at front counter
            with self.associate.request() as associate_req:
                yield associate_req
                yield self.env.timeout(random.triangular(1, 2, 1.5)) 
                customer_record["Ordered_time"] = self.env.now
                print(f"{customer_id} ordered (Counter) at {self.env.now:.2f}")
        else: #online
                yield self.env.timeout(0.5) 
                customer_record["Ordered_time"] = self.env.now
                print(f"{customer_id} ordered (Kiosk) at {self.env.now:.2f}")
    
        self.env.process(self.kitchen_production(customer_id, customer_record))

    def kitchen_production(self, customer_id, customer_record):
        with self.cook.request() as cook_req:
            yield cook_req
            yield self.env.timeout(random.triangular(2, 4, 3))
            customer_record["Production_time"] = self.env.now
            print(f"For {customer_id} production done at {self.env.now:.2f}")
        
        self.env.process(self.packing(customer_id, customer_record))
#Assembling burgers and packing
    def packing(self, customer_id, customer_record):
            packing_req = self.order_fullfillment.request()
            
            # Packing is slammed >2 AND Front Counter is relatively free <1 #Effective utilization of resources
            if len(self.order_fullfillment.queue) > 2 and len(self.associate.queue) < 1:
                associate_req = self.associate.request()
                result = yield packing_req | associate_req # Wait untill either of the resrce is available
                
                if associate_req in result:
                    # The Front Counter Associate helped!
                    used_resource = self.associate
                    used_req = associate_req
                    packing_req.cancel() # Stop waiting for the packer
                else:
                    # The Packing Associate finished first
                    used_resource = self.order_fullfillment
                    used_req = packing_req
                    associate_req.cancel() # Stop waiting for the associate
            else:
                # Normal operation: only wait for the packing associate
                yield packing_req
                used_resource = self.order_fullfillment
                used_req = packing_req

    
            yield self.env.timeout(random.triangular(1,2,1.5))
            customer_record["order_fullfillment"] = self.env.now

            used_resource.release(used_req) #Manually release the resource since we didn't use 'with'

            print(f"For {customer_id} order_fullfilled at {self.env.now:.2f}")
            self.env.process(self.dinein(customer_id, customer_record))

    def dinein(self, customer_id, customer_record):
        if random.random() < 0.60:
            # Grab and go
            customer_record["Hand-off/Exit"] = self.env.now
            print(f"For {customer_id} exit (Takeaway) at {self.env.now:.2f}")
        else:
            # Eat in
            yield self.env.timeout(random.triangular(25, 30, 40)) 
            customer_record["Hand-off/Exit"] = self.env.now
            print(f"For {customer_id} exit (Dine-in) at {self.env.now:.2f}")
random.seed(42)
# Setup and Run
env = simpy.Environment()
obj1 = FastFoodchain(env, arrival_rate)
env.process(obj1.arrivalrate())
env.process(obj1.monitor_resources())
env.run(until=1200) # Run for 20 hours 

