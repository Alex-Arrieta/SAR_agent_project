import pytest
from src.sar_project.agents.logisitics_agent import LogisticsAgent, Supplier, Mission, Hub

class TestLogisticAgent:
    @pytest.fixture
    def agent(self):
        return LogisticsAgent()

    def test_initialization(self, agent):
        assert agent.name == "logistics_specialist"
        assert agent.role == "Logistics Specialist"
        assert agent.mission_status == "standby"

    def test_graph_making(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub = Hub("hub1")
        mission = Mission("mission1")
        graph.add_supplier(supplier)
        graph.add_hub(hub)
        graph.add_mission(mission)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        nodes = agent.get_graph().get_nodes()
        assert nodes[0] == supplier
        assert nodes[1] == hub
        assert nodes[2] == mission
        assert nodes[0].get_provided_goods() == ["Rope"]
        assert nodes[2].get_required_goods() == {"Rope":1}

    def test_graph_pathing_empty(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub = Hub("hub1")
        mission = Mission("mission1")
        graph.add_supplier(supplier)
        graph.add_hub(hub)
        graph.add_mission(mission)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        assert agent.calculate_deliveries() == "Unable to find path for mission mission1"

    def test_graph_pathing_fail(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub = Hub("hub1")
        mission = Mission("mission1")
        supplier.update_connections(hub, 2)
        hub.update_connections(supplier, 2)
        graph.add_supplier(supplier)
        graph.add_hub(hub)
        graph.add_mission(mission)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        assert agent.calculate_deliveries() == "Unable to find path for mission mission1"
        
    def test_graph_pathing_success(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub = Hub("hub1")
        mission = Mission("mission1")
        supplier.update_connections(hub, 2)
        hub.update_connections(supplier, 2)
        hub.update_connections(mission, 2)
        mission.update_connections(hub, 2)
        graph.add_supplier(supplier)
        graph.add_hub(hub)
        graph.add_mission(mission)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        assert agent.calculate_deliveries() == {mission : {"Rope" : [supplier, hub, mission]}}

    def test_graph_pathing_success_opt(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub1 = Hub("hub1")
        hub2 = Hub("hub2")
        mission = Mission("mission1")
        supplier.update_connections(hub1, 3)
        hub1.update_connections(supplier, 3)
        supplier.update_connections(hub2, 2)
        hub2.update_connections(supplier, 2)
        hub1.update_connections(mission, 2)
        mission.update_connections(hub1, 2)
        hub2.update_connections(mission, 2)
        mission.update_connections(hub2, 2)
        graph.add_supplier(supplier)
        graph.add_hub(hub1)
        graph.add_mission(mission)
        graph.add_hub(hub2)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        assert agent.calculate_deliveries() == {mission : {"Rope" : [supplier, hub2, mission]}}

    def test_graph_pathing_time_step(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub1 = Hub("hub1")
        hub2 = Hub("hub2")
        mission = Mission("mission1")
        supplier.update_connections(hub1, 3)
        hub1.update_connections(supplier, 3)
        supplier.update_connections(hub2, 2)
        hub2.update_connections(supplier, 2)
        hub1.update_connections(mission, 2)
        mission.update_connections(hub1, 2)
        hub2.update_connections(mission, 2)
        mission.update_connections(hub2, 2)
        graph.add_supplier(supplier)
        graph.add_hub(hub1)
        graph.add_mission(mission)
        graph.add_hub(hub2)
        supplier.add_provided_good("Rope")
        mission.add_required_good("Rope", 1)
        agent.run_time_tick()
        assert graph.get_good_transit()[0] == ("Rope", supplier, hub2, 10, [supplier, hub2, mission], 0)
        assert mission.get_required_goods() == {}
        agent.run_time_tick()
        assert graph.get_good_transit() == [("Rope", supplier, hub2, 10, [supplier, hub2, mission], 0)]
        agent.run_time_tick()
        assert graph.get_good_transit()[0] == ("Rope", hub2, mission, 10, [supplier, hub2, mission], 2)
        agent.run_time_tick()
        assert graph.get_good_transit() == [("Rope", hub2, mission, 10, [supplier, hub2, mission], 2)]
        agent.run_time_tick()
        assert graph.get_good_transit() == []
        assert mission.get_curr_store() == {"Rope" : 10}

    def test_graph_custom_path(self, agent):
        graph = agent.get_graph()
        supplier = Supplier("supply1")
        hub1 = Hub("hub1")
        hub2 = Hub("hub2")
        mission = Mission("mission1")
        supplier.update_connections(hub1, 3)
        hub1.update_connections(supplier, 3)
        supplier.update_connections(hub2, 2)
        hub2.update_connections(supplier, 2)
        hub1.update_connections(mission, 2)
        mission.update_connections(hub1, 2)
        hub2.update_connections(mission, 2)
        mission.update_connections(hub2, 2)
        graph.add_supplier(supplier)
        graph.add_hub(hub1)
        graph.add_mission(mission)
        graph.add_hub(hub2)
        supplier.add_provided_good("Rope")
        supplier.add_provided_good("Steel")
        mission.add_required_good("Rope", 1)
        agent.run_time_tick()
        assert graph.get_good_transit()[0] == ("Rope", supplier, hub2, 10, [supplier, hub2, mission], 0)
        assert mission.get_required_goods() == {}
        agent.run_time_tick()
        assert graph.get_good_transit() == [("Rope", supplier, hub2, 10, [supplier, hub2, mission], 0)]
        agent.make_delivery("Steel", 10, [supplier, hub1])
        agent.run_time_tick()
        assert graph.get_good_transit()[1] == ("Rope", hub2, mission, 10, [supplier, hub2, mission], 2)
        assert graph.get_good_transit()[0] == ("Steel", supplier, hub1, 10, [supplier, hub1], 2)