from .base_agent import SARBaseAgent
import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))


class Supplier():
    def __init__(self, name):
        self.name = name
        self.provides = []
        self.connections = {} # connected to, weight

    def get_name(self):
        return self.name
    
    def get_connections(self):
        return self.connections
    
    def update_connections(self, to_connect, weight):
        self.connections[to_connect] = weight

    def remove_connection(self, to_disconnect):
        del self.connections[to_disconnect]
    
    def get_provided_goods(self):
        return self.provides

    def add_provided_good(self, good): #goods are strings?
        self.provides.append(good)

    def remove_provided_good(self, good):
        self.provides.remove(good)

    def ship_good(self, good, destination, amt):
        destination.recieve_good(good, amt) # Need way to add delay

class Mission():
    def __init__(self, name):
        self.name = name
        self.requires = {} #key: good and value: amt
        self.has = {}
        self.consuptionRate = {} # maybe calculate consumption rate over steps
        self.connections = {}

    def get_name(self):
        return self.name
    
    def get_connections(self):
        return self.connections
    
    def update_connections(self, to_connect, weight):
        self.connections[to_connect] = weight

    def remove_connection(self, to_disconnect):
        del self.connections[to_disconnect]

    def add_required_good(self, good, amt): #goods are strings?
        self.requires[good] = amt
    
    def remove_required_good(self, good): #just in case
        del self.requires[good]

    def get_required_goods(self):
        return self.requires

    def recieve_good(self, good, amount):
        if good in self.requires:
            currAmount = self.requires[good] - amount
            if currAmount < 0:
                del self.requires[good]
                self.has["good"] = -currAmount
            else:
                self.requires[good] = currAmount
        if good in self.has:
            self.has["good"] = self.has["good"] + amount
        else:
            self.has["good"] = amount
            

class Hub():
    def __init__(self, name):
        self.name = name
        self.has = {}
        self.connections = {}

    def get_name(self):
        return self.name
    
    def get_connections(self):
        return self.connections
    
    def update_connections(self, to_connect, weight):
        self.connections[to_connect] = weight

    def remove_connection(self, to_disconnect):
        del self.connections[to_disconnect]

    def get_goods(self):
        return self.has

    def recieve_good(self, good, amount):
        if good in self.has:
            self.has["good"] = self.has["good"] + amount
        else:
            self.has["good"] = amount

    def ship_good(self, good, destination, amt):
        amt = min(amt, self.has[good])
        self.has[good] = self.has[good] - amt
        destination.recieve_good(good, amt) # Need way to add delay, perhaps have a waiting array w/ items in transit.
        

class LogisticsGraph():
    def __init__(self):
        self.suppliers = []
        self.hubs = []
        self.missions = []

    def get_nodes(self):
        nodes = self.suppliers + self.hubs + self.missions
        return nodes

    def add_supplier(self, supplier):
        self.suppliers.append(supplier)

    def remove_supplier(self, supplier):
        self.suppliers.remove(supplier)

    def get_suppliers(self):
        return self.suppliers

    def add_hub(self, hub):
        self.hubs.append(hub)

    def remove_hub(self, hub):
        self.hubs.remove(hub)

    def get_hubs(self):
        return self.hubs

    def add_mission(self, mission):
        self.missions.append(mission)

    def remove_mission(self, mission):
        self.missions.remove(mission)

    def get_missions(self):
        return self.missions


class LogisticsAgent(SARBaseAgent):
    def __init__(self, name="logistics_specialist"):
        super().__init__(
            name=name,
            role="Logistics Specialist",
            system_message="""You are a Logistics specialist for SAR operations. Your role is to:
            1. Analyze logistic requests
            2. Predict weather impacts on operations
            3. Provide equipment recommendations
            4. Monitor changing conditions"""
        )
        self.graph = LogisticsGraph()
        
    def process_request(self, message):
        """Process logistics-related requests"""
        try:
            # Example processing logic
            if "get_requests" in message:
                return self.get_requests()
            elif "get_deliveries" in message:
                return self.get_deliveries()
            elif "assess_risk" in message:
                return self.assess_weather_risk(message["location"])
            else:
                return {"error": "Unknown request type"}
        except Exception as e:
            return {"error": str(e)}
        
    def get_graph(self):
        return self.graph
        
    def update_graph(self, new_request):
        return -1

    def get_requests(self):
        requests = []
        for mission in self.graph.get_missions():
            requests.append((mission.get_name(), mission.get_required_goods()))
        return requests
    
    def calculate_deliveries(self, method = "dijkstra"):
        paths = []
        if method == "dijkstra":
            for mission in self.graph.get_missions():
                reqs = mission.get_required_goods()
                for req in reqs:
                    for supplier in self.graph.get_suppliers():
                        if req in supplier.get_provided_goods():
                            nodes = {node:None for node in self.graph.get_nodes()}
                            visited_nodes = {node:100000 for node in self.graph.get_nodes()}
                            unvisited_nodes = {node:100000 for node in self.graph.get_nodes()}
                            unvisited_nodes[supplier] = 0
                            visited_nodes[supplier] = 0
                            currNode = supplier
                            while currNode != mission:
                                visited_nodes[currNode] = unvisited_nodes[currNode]
                                del unvisited_nodes[currNode]
                                connections = currNode.get_connections()
                                for node in connections:
                                    if node in unvisited_nodes:
                                        dist = visited_nodes[currNode] + connections[node]
                                        if dist < unvisited_nodes[node]:
                                            nodes[node] = currNode
                                            unvisited_nodes[node] = dist
                                min_dist = 100000000
                                for node in unvisited_nodes:
                                    if unvisited_nodes[node] < min_dist:
                                        min_dist = unvisited_nodes[node]
                                        currNode = node
                                if min_dist >= 100000:
                                    return "Unable to find path for mission " + mission.get_name()
                            path = []
                            while currNode != None:
                                path.append(currNode)
                                currNode = nodes[currNode]
                            paths.append(path)
            return paths            
        return -1

    def _generate_recommendations(self, risks):
        """Generate safety recommendations based on risks"""
        recommendations = []
        for risk in risks:
            if risk == "high_wind":
                recommendations.append("Secure loose equipment")
            elif risk == "low_visibility":
                recommendations.append("Use additional lighting")
        return recommendations

    def update_status(self, status):
        """Update the agent's status"""
        self.status = status
        return {"status": "updated", "new_status": status}

    def get_status(self):
        """Get the agent's current status"""
        return getattr(self, "status", "unknown")
