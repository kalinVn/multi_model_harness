import unittest
from unittest.mock import Mock

from harness.factory.agents_factory import AgentFactory
from harness.registry.agent_registry import AgentRegistry
from harness.skills.skill_registry import SkillRegistry


class AgentFactoryRegistryTests(unittest.TestCase):
    def setUp(self):
        self.factory = AgentFactory(Mock(), Mock(), [], SkillRegistry())

    def test_factory_creates_independent_planners_with_unique_stable_ids(self):
        first = self.factory.create_planner()
        second = self.factory.create_planner()
        first_id = first.agent_id

        self.assertNotEqual(first.agent_id, second.agent_id)
        self.assertEqual(first.agent_id, first_id)
        self.assertEqual(first.agent_type, "planner")
        self.assertEqual(second.agent_type, "planner")

    def test_registry_stores_retrieves_and_filters_multiple_planners(self):
        registry = AgentRegistry()
        first = self.factory.create_planner()
        second = self.factory.create_planner()

        registry.register(first)
        registry.register(second)

        self.assertIs(registry.get(first.agent_id), first)
        self.assertIs(registry.get(second.agent_id), second)
        self.assertEqual(registry.get_by_type("planner"), [first, second])
        self.assertEqual(registry.list_agents(), [first, second])

    def test_registry_rejects_duplicate_agent_ids(self):
        registry = AgentRegistry()
        planner = self.factory.create_planner()
        registry.register(planner)

        with self.assertRaisesRegex(ValueError, planner.agent_id):
            registry.register(planner)

    def test_registry_unregisters_agent(self):
        registry = AgentRegistry()
        planner = self.factory.create_planner()
        registry.register(planner)

        registry.unregister(planner.agent_id)

        self.assertEqual(registry.list_agents(), [])
        with self.assertRaisesRegex(ValueError, f"Unknown agent: {planner.agent_id}"):
            registry.get(planner.agent_id)


if __name__ == "__main__":
    unittest.main()
