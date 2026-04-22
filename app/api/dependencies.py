from app.services.analytics import AnalyticsService


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
