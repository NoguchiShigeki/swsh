import openai
from swarm import Swarm, Agent
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
client = Swarm()

# Define the number of agents and debate rounds
agent_number = int(input("Enter the number of agents: "))
debate_round_number = int(input("Enter the number of debate rounds: "))

# Start of the time
start = time.time()

# Create a list to store agent instances
agents = []

# Dynamically create agents in a loop
for i in range(agent_number):
    agent = Agent(
        name=f"Agent {i+1}",
        # If you want to add a persona to the agents, you can change the instructions here, e.g., "Pretend that you are a very creative person."
        instructions=f"You are agent {i+1}. You are one of the agents in a multi-agent system."
        # You will generate your initial response to the user input, interact with other agents' responses, and update your own response multiple times. Finally, you will provide a conclusion.
    )
    agents.append(agent)

# The aggregator: This is used to aggregate the responses of agents in the final round.
aggregator = Agent(
    name="Aggregator",
    instructions=(
        "You are part of a Collaborative Debate Model, a multi-agent system where agents independently propose solutions and critique each other's responses over multiple rounds. "
        "Your role is to aggregate the final responses from all agents in the last round. "
        "Collect and analyze the responses to find the majority opinion or pattern, and prepare the final aggregated answer."
    )
)

# The grader: This is required for the grading of the multi-agent system
grader = Agent(
    name="Grader",
    instructions=(
        "You are part of a Collaborative Debate Model, a multi-agent system where agents propose solutions and refine their answers through multiple rounds of debate. "
        "Compare the final answer with the correct answer and determine whether it is correct ('True') or incorrect ('False')."
    )
)

# These instructions are used in the messages for the agents during execution
instruction_initial = "Make sure to state your answer at the end of the response."
instruction_debate_1 = "These are the recent/updated opinions from other agents:"
instruction_debate_2 = "Use these opinions carefully as additional advice, and provide an updated answer. Make sure to state your answer at the end of the response."

# Define the initial user message
user_input = [{"role": "user", "content": f"Tom has a red marble, a green marble, a blue marble, and three identical yellow marbles. How many different groups of two marbles can Tom choose? {instruction_initial}"}]
label = "The answer is 7 different groups."

# Global conversation history with the initial user message
conversation_history = [{"name": "User", "role": "user", "content": user_input[0]["content"], "round": 0}]

# Dictionary list to store all responses made by agents
all_responses = []

# Loop through the debates and come to a conclusion over the specified number of debate rounds
for j in range(debate_round_number):
    if j == 0:
        # Loop through the agents to generate their first responses to the user input
        for i in range(agent_number):
            # Pass the entire conversation history to each agent
            response = client.run(
                agent=agents[i],
                messages=user_input
            )

            # Add the latest agent's response to the list of all_responses
            all_responses.append({
                "name": agents[i].name,
                "role": "assistant",
                "content": response.messages[-1]["content"],
                "round": j+1  # Round 1
            })

            # Add the latest agent's response to the conversation history
            conversation_history.append({
                "name": agents[i].name,
                "role": "assistant",
                "content": response.messages[-1]["content"],
                "round": j+1  # Round 1
            })

    else:
        # Loop through the agents to generate updated responses to the user input
        for i in range(agent_number):
            # Search for the responses from the previous round, excluding the current agent's response
            last_round_others_responses = [
                response for response in all_responses if response["round"] == j and response["name"] != agents[i].name
            ]

            # Find the current agent's last response to allow for self-reflection
            last_round_own_response = [
                response for response in all_responses if response["round"] == j and response["name"] == agents[i].name
            ]

            # Create a self-reflection message if the agent's previous response exists
            if last_round_own_response:
                self_reflection_message = f"Your previous response was: {last_round_own_response[0]['content']}. Reflect on your own response and improve it."

            # Update the messages for the current agent by incorporating the previous round's responses from other agents
            previous_responses_message = "\n".join([f"{resp['name']}: {resp['content']}" for resp in last_round_others_responses])
            user_input_with_debate = [{"role": "user", "content": f"{instruction_debate_1} {previous_responses_message}\n\n{self_reflection_message}\n\n{instruction_debate_2}"}]

            # Pass the previous agents' responses to the current agent
            response = client.run(
                agent=agents[i],
                messages=user_input_with_debate  # Updated with other agents' responses
            )

            # Add the latest agent's response to the list of all_responses
            all_responses.append({
                "name": agents[i].name,
                "role": "assistant",
                "content": response.messages[-1]["content"],
                "round": j+1  # Current round
            })

            # Add the latest agent's response to the conversation history
            conversation_history.append({
                "name": agents[i].name,
                "role": "assistant",
                "content": response.messages[-1]["content"],
                "round": j+1  # Current round
            })

# Aggregating the final round's responses
instruction_aggregate = "You are going to conclude the debate by aggregating all agents' responses into a single conclusion."
final_round_response = [
    response for response in all_responses if response["round"] == debate_round_number
]
final_round_response_message = "\n".join([f"{resp['name']}: {resp['content']}" for resp in final_round_response])
input_final_round_response = [{"role": "user", "content": f"{instruction_aggregate}\n\n{final_round_response_message}"}]
aggregator_response = client.run(
    agent=aggregator,
    messages=input_final_round_response
)

# The final response from the aggregator
conclusion = aggregator_response.messages[-1]["content"]
print("The conclusion from the final agent:\n", conclusion)

# Grading process
grading_messages = [
    {"role": "system", "content": "You are tasked with grading the answer."},
    {"role": "user", "content": f"Answer: {label}"},
    {"role": "assistant", "content": conclusion}
]

grading_response = client.run(
    agent=grader,
    messages=grading_messages
)

# Grading result
grading_result = grading_response.messages[-1]["content"]

print("Label:", label)
print("Grading result:", grading_result)

# Calculate elapsed time
end = time.time()
elapsed_time = end - start
print("Elapsed time:", elapsed_time)

# Optional: Print conversation history with agent names if needed
# print("\n--- Conversation History ---")
# for entry in conversation_history:
#     print(f"{entry['name']} ({entry['role']}):\n{entry['content']}\nRound: {entry['round']}")
