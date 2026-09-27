"""Service computing maintenance health and remaining intervals for assets."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.maintenance import log_repo, rule_repo
from app.schemas.enums import MaintenanceStatus, MetricType
from app.schemas.health import AssetHealthReport, MaintenanceHealthItem


class MaintenanceSchedulerService:
    """Calculates preventive maintenance thresholds against dynamic asset telemetry."""

    @staticmethod
    def _compute_status(consumed: float, interval: float) -> MaintenanceStatus:
        """Categorize health based on consumed ratio.

        Intent:
            90% threshold marks a warning (DUE_SOON) to give the user advance notice
            before reaching 100% (OVERDUE).
        """
        if interval <= 0:
            return MaintenanceStatus.OVERDUE
        ratio = consumed / interval
        if ratio >= 1.0:
            return MaintenanceStatus.OVERDUE
        if ratio >= 0.9:
            return MaintenanceStatus.DUE_SOON
        return MaintenanceStatus.OK

    def evaluate_asset_health(self, db: Session, *, asset: Asset) -> AssetHealthReport:
        """Evaluate all active maintenance rules for an asset."""
        rules = rule_repo.get_by_asset(db, asset_id=asset.id)
        now_utc = datetime.now(timezone.utc)

        items: list[MaintenanceHealthItem] = []
        overall = MaintenanceStatus.OK

        for rule in rules:
            latest_log = log_repo.get_latest_for_type(
                db, asset_id=asset.id, maintenance_type=rule.maintenance_type
            )

            consumed = 0.0
            current_reading = 0.0
            last_date: datetime | None = None
            last_metric: float | None = None

            if rule.metric_type == MetricType.ODOMETER:
                current_reading = float(
                    asset.metadata_payload.get("last_odometer", 0.0)
                )
                if latest_log and latest_log.metric_value_at_service is not None:
                    last_metric = latest_log.metric_value_at_service
                    last_date = latest_log.service_date
                    consumed = max(0.0, current_reading - last_metric)
                else:
                    consumed = current_reading

            elif rule.metric_type == MetricType.TIME_DAYS:
                base_date = latest_log.service_date if latest_log else asset.created_at
                last_date = latest_log.service_date if latest_log else None
                delta = now_utc - base_date
                consumed = max(0.0, float(delta.days))
                current_reading = consumed

            elif rule.metric_type == MetricType.TIME_MONTHS:
                base_date = latest_log.service_date if latest_log else asset.created_at
                last_date = latest_log.service_date if latest_log else None
                delta = now_utc - base_date
                # Approximate 30.4375 days per month
                consumed = max(0.0, delta.days / 30.4375)
                current_reading = round(consumed, 1)

            elif rule.metric_type == MetricType.USAGE_HOURS:
                current_reading = float(
                    asset.metadata_payload.get("usage_hours", 0.0)
                )
                if latest_log and latest_log.metric_value_at_service is not None:
                    last_metric = latest_log.metric_value_at_service
                    last_date = latest_log.service_date
                    consumed = max(0.0, current_reading - last_metric)
                else:
                    consumed = current_reading

            status = self._compute_status(consumed, rule.interval_value)
            percentage = min(100.0, round((consumed / rule.interval_value) * 100, 1)) if rule.interval_value > 0 else 100.0
            remaining = max(0.0, round(rule.interval_value - consumed, 1))

            if status == MaintenanceStatus.OVERDUE:
                overall = MaintenanceStatus.OVERDUE
            elif status == MaintenanceStatus.DUE_SOON and overall != MaintenanceStatus.OVERDUE:
                overall = MaintenanceStatus.DUE_SOON

            items.append(
                MaintenanceHealthItem(
                    rule_id=rule.id,
                    maintenance_type=rule.maintenance_type,
                    metric_type=rule.metric_type,
                    interval_value=rule.interval_value,
                    metric_unit=rule.metric_unit,
                    current_reading=round(current_reading, 1),
                    last_service_date=last_date,
                    last_service_metric=last_metric,
                    remaining_value=remaining,
                    percentage_used=percentage,
                    status=status,
                )
            )

        return AssetHealthReport(
            asset_id=asset.id,
            asset_name=asset.name,
            overall_status=overall,
            rules_count=len(rules),
            items=items,
        )


scheduler_service = MaintenanceSchedulerService()
