"""
Sample Metaflow that generates various DataFrames for visualization testing.
This flow simulates an e-commerce data analysis pipeline.
"""

from metaflow import FlowSpec, step, current
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class ECommerceAnalysisFlow(FlowSpec):
    """
    A flow that generates sample e-commerce data and performs analysis,
    creating different types of DataFrames at various steps.
    """

    @step
    def start(self):
        """Generate sample sales data."""
        # Create sample sales data
        np.random.seed(42)
        n_records = 1000

        # Generate dates for the last 30 days
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]

        self.sales_df = pd.DataFrame(
            {
                "date": np.random.choice(dates, n_records),
                "product_id": np.random.randint(1, 51, n_records),
                "customer_id": np.random.randint(1, 201, n_records),
                "quantity": np.random.randint(1, 11, n_records),
                "unit_price": np.random.uniform(10, 1000, n_records).round(2),
                "region": np.random.choice(
                    ["North", "South", "East", "West"], n_records
                ),
            }
        )

        # Calculate total price
        self.sales_df["total_price"] = (
            self.sales_df["quantity"] * self.sales_df["unit_price"]
        )

        # Sort by date
        self.sales_df = self.sales_df.sort_values("date")

        self.next(self.daily_analysis)

    @step
    def daily_analysis(self):
        """Perform daily sales analysis."""
        # Daily sales summary
        self.daily_sales = (
            self.sales_df.groupby("date")
            .agg({"total_price": "sum", "quantity": "sum", "customer_id": "nunique"})
            .reset_index()
        )

        self.daily_sales.columns = [
            "date",
            "daily_revenue",
            "items_sold",
            "unique_customers",
        ]

        # Regional analysis
        self.regional_sales = (
            self.sales_df.groupby("region")
            .agg({"total_price": "sum", "quantity": "sum", "customer_id": "nunique"})
            .reset_index()
        )

        self.next(self.customer_analysis)

    @step
    def customer_analysis(self):
        """Analyze customer behavior."""
        # Customer purchase history
        self.customer_stats = (
            self.sales_df.groupby("customer_id")
            .agg({"total_price": ["sum", "mean", "count"], "quantity": "sum"})
            .reset_index()
        )

        self.customer_stats.columns = [
            "customer_id",
            "total_spent",
            "avg_order_value",
            "number_of_orders",
            "total_items_bought",
        ]

        # Add customer segments
        self.customer_stats["segment"] = pd.qcut(
            self.customer_stats["total_spent"],
            q=4,
            labels=["Bronze", "Silver", "Gold", "Platinum"],
        )

        self.next(self.product_analysis)

    @step
    def product_analysis(self):
        """Analyze product performance."""
        # Product performance metrics
        self.product_stats = (
            self.sales_df.groupby("product_id")
            .agg(
                {
                    "total_price": ["sum", "mean"],
                    "quantity": "sum",
                    "customer_id": "nunique",
                }
            )
            .reset_index()
        )

        self.product_stats.columns = [
            "product_id",
            "total_revenue",
            "avg_price",
            "units_sold",
            "unique_customers",
        ]

        # Calculate product ranking
        self.product_stats["revenue_rank"] = self.product_stats["total_revenue"].rank(
            ascending=False
        )

        self.next(self.create_summary)

    @step
    def create_summary(self):
        """Create summary dashboard data."""
        # Overall summary metrics
        total_revenue = self.sales_df["total_price"].sum()
        total_orders = len(self.sales_df)
        total_customers = self.sales_df["customer_id"].nunique()

        self.summary_stats = pd.DataFrame(
            {
                "metric": [
                    "Total Revenue",
                    "Total Orders",
                    "Total Customers",
                    "Avg Order Value",
                    "Items per Order",
                ],
                "value": [
                    total_revenue,
                    total_orders,
                    total_customers,
                    total_revenue / total_orders,
                    self.sales_df["quantity"].sum() / total_orders,
                ],
            }
        )

        self.next(self.end)

    @step
    def end(self):
        """End of flow."""
        print("Flow completed successfully!")
        print(f"Created {len(self.sales_df)} sample sales records")
        print(
            f"Generated {self.customer_stats['customer_id'].nunique()} customer profiles"
        )
        print(f"Analyzed {self.product_stats['product_id'].nunique()} products")


if __name__ == "__main__":
    ECommerceAnalysisFlow()
