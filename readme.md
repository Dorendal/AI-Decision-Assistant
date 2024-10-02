# README

This Python script uses propositional logic to determine the most appropriate commuting option (Work from Home, Drive, Public Transport) based on various conditions such as rain, traffic, appointments, etc. The script defines a series of logical rules that are added to a knowledge base, and then checks different commuting options based on given conditions.

### Key Features:

1. **Conditions**:
   - **Rain**: It's raining.
   - **HeavyTraffic**: Traffic is heavy.
   - **EarlyMeeting**: You have early meetings.
   - **Strike**: There's a public transport strike.
   - **Appointment**: You have a doctor's appointment.
   - **RoadConstruction**: There's road construction.

2. **Commuting Options**:
   - **WFH**: Work from Home.
   - **Drive**: Drive to the office.
   - **PublicTransport**: Take public transport.

3. **Defined Rules**:
   - **Rule 1**: If it's raining or you have an early meeting, you should work from home.
   - **Rule 2**: If it's not raining and traffic is not heavy, you should drive.
   - **Rule 3**: If there's no strike and it's not raining, you should take public transport.
   - **Rule 4**: If you have a doctor's appointment, you should drive.
   - **Rule 5**: If there's road construction, you should avoid driving.

4. **Scenario Checking**:
   The `check_scenario` function allows you to test different scenarios based on specified conditions. It evaluates which commuting options are logically valid for each scenario based on the knowledge base.

### Tested Scenarios:

- **Scenario 1**: It's raining and traffic is heavy.
- **Scenario 2**: There's a public transport strike, but it's not raining.
- **Scenario 3**: It's not raining, traffic is light, and there’s no strike.
- **Scenario 4**: There’s road construction, and you have a doctor’s appointment.

For each scenario, the script determines whether it's better to work from home, drive, or take public transport, using model checking (`model_check`).

### Usage:
Run the script to see commuting recommendations based on different combinations of conditions.