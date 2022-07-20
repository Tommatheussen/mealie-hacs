"""MealieEntity class"""
from __future__ import annotations
from abc import abstractmethod


from homeassistant.const import CONF_HOST, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .models import MealieData, Recipe
from .const import DOMAIN, ICONS, NAME


class MealieEntity(CoordinatorEntity[DataUpdateCoordinator[MealieData]]):
    """mealie Entity class."""

    def __init__(self, coordinator: DataUpdateCoordinator[MealieData]) -> None:
        """Initialize the Mealie entity"""
        super().__init__(coordinator)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.data.get(CONF_USERNAME),
            sw_version=self.coordinator.data.about.version,
            manufacturer=NAME,
            configuration_url=self.coordinator.config_entry.data.get(CONF_HOST),
            suggested_area="Kitchen",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._process_update()
        super()._handle_coordinator_update()

    @callback
    @abstractmethod
    def _process_update(self) -> None:
        """Process an update from the coordinator"""


class MealPlanEntity(MealieEntity):
    """mealie Meal Plan Entity class."""

    def __init__(self, meal, coordinator):
        super().__init__(
            coordinator,
        )

        self.meal = meal
        self.recipe: Recipe | None = None

        self._attr_unique_id = self.meal
        self._attr_name = f"Meal plan {self.meal}"
        self._attr_icon = ICONS.get(self.meal)

        self._process_update()

    @callback
    def _process_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.recipe = next(
            (
                mealPlan.recipe
                for mealPlan in self.coordinator.data.mealPlans
                if mealPlan.entryType == self.meal
            ),
            None,
        )
