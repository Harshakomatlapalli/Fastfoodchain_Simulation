# Fast Food Chain Operations Simulation

Fastfood chain Operations & Discrete Event Simulation
A specialized Discrete Event Simulation (DES) built to analyze and optimize service delivery in a high-volume restaurant environment. This model focuses on identifying bottlenecks in the order-to-fulfillment pipeline and testing process improvement interventions.

This project simulates 20 hours of restaurant operations, modeling the stochastic nature of customer arrivals and the multi-stage fulfillment process. It compares a baseline operation against improved scenarios to determine the impact of automation and resource flexibility on queue lengths and resource utilization.

Project Structure
Plaintext
mcdonalds-simulation/
- data/               # Input parameters (arrival_rates.csv)
- src/                # Core simulation logic (Fastfood class and methods)
- notebooks/          # Exploratory analysis and visualization
- tests/              # Unit tests for arrival rate logic
- requirements.txt    # Dependency list with specific versions
- README.md           # Project documentation

Requirements & Installation
This simulation requires Python 3.9+ and the following libraries:

simpy==4.1.1 (Discrete event engine)

pandas==2.2.3 (Data structuring)

numpy==2.2.0 (Statistical distributions)

matplotlib==3.10.0 & seaborn==0.13.2 (Visualization)

To install, run:

Bash
pip install -r requirements.txt

Key Performance Indicators (KPIs)
The model tracks the following metrics to evaluate performance:

Hourly Utilization Rates: Percentage of time the Counter, Kitchen, and Packing associates are busy.

Queue Lengths: Real-time monitoring of the Production and Fulfillment queues.

Balking Rate: The percentage of customers who leave the system when the queue exceeds threshold limits.



Scenarios & Improvements Tested
The simulation was used to evaluate below operational "What-If" scenarios:

Resource Cross-Training: Implemented logic where the Front Counter Associate assists with Packing when fulfillment queues exceed 2 orders and the counter is idle.

Process Automation: Tested the impact of Automated Labeling in the packing stage, reducing the triangular distribution time for fulfillment from (1, 2, 1.5) to (1, 1.5, 1.5).

Capacity Expansion: Analyzed the effect of adding a third cook during peak hours identified by the arrival_rates.csv.

🚀 How to Run
Navigate to the notebooks/ folder.

Open exploratory_sim.ipynb.

The notebook is configured to load data from data/arrival_rates.csv and import the engine from src/simulation.py.

Run all cells to generate the utilization heatmaps and queue length charts.
