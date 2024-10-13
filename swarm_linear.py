import openai
from swarm import Swarm, Agent
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
client = Swarm()

# Define the number of generations
agent_generations = int(input("Enter the number of agent generations: "))

# Create a list to store agent instances
agents = []

# Dynamically create agents in a loop
for i in range(agent_generations):
    if i == agent_generations - 1:
        # The last agent generates the conclusion (like the original agent_3)
        agent = Agent(
            name=f"Agent {i+1}",
            instructions="You are the final node. Generate the conclusion based on the previous agents' responses."
        )
    else:
        # Other agents reflect on the previous agents' responses
        agent = Agent(
            name=f"Agent {i+1}",
            instructions=f"You are node {i+1}. Reflect on the user inputs and the previous agents' responses, then generate a new response."
        )
    agents.append(agent)

# The grader
grader = Agent(
    name="Grader",
    instructions="You are a grader of the answers. Compare the Agents' responses with the correct answer and grade them. If the answer is correct, output 'True', otherwise 'False'."
)

# Define initial user message
messages = [{"role": "user", "content": "Tom has a red marble, a green marble, a blue marble, and three identical yellow marbles. How many different groups of two marbles can Tom choose?"}]
label = "The answer is 7."

# Conversation history with the initial user message
conversation_history = [{"name": "User", "role": "user", "content": messages[0]["content"]}]

# Loop through the agents to generate responses
for i in range(agent_generations):
    response = client.run(
        agent=agents[i],
        messages=messages  # Use the entire conversation history
    )

    # Add the latest agent's response to the conversation history
    conversation_history.append({
        "name": agents[i].name,
        "role": "assistant",
        "content": response.messages[-1]["content"]
    })

    # Update the messages to include the latest conversation for the next agent
    messages = [{"role": "user", "content": messages[0]["content"]}] + [{"role": "assistant", "content": entry["content"]} for entry in conversation_history[1:]]

# The final response from the last agent
final_response = conversation_history[-1]["content"]
print("The conclusion from the final agent:\n", final_response)

# The grading process
grading_messages = [
    {"role": "system", "content": "You are tasked with grading the answer."},
    {"role": "user", "content": "Answer: " + label},
    {"role": "assistant", "content": final_response}
]

grading = client.run(
    agent=grader,
    messages=grading_messages
)

# Grading result
grading_result = grading.messages[-1]["content"]

print("Grading result:", grading_result)

# Print conversation history with agent names if needed
# print("\n--- Conversation History ---")
# for entry in conversation_history:
#     print(f"{entry['name']} ({entry['role']}):\n{entry['content']}\n")
