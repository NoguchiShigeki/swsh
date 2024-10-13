How to execute:
1. Fullfil the requirements in activated venv
```shell
pip install -r requirements.txt
```
2. Set up the .venv by changing a placeholder string with your OpenAI API Key (Google the how to issue a api key in OpenAI)
```.env
OPENAI_API_KEY=sk-proj--your-openai-api-key
```
3. Execute "swarm_linear.py"
```shell
python3 swarm_linear.py
```
4. You will be asked to input the number of agents.
```shell
Enter the number of agent generations:
```
5. The program will do the thing.
Output shows the final agent's conclusion and the grading result (True or False) which is based on the correctness of the conclusion.

Output:
```shell
The conclusion from the final agent:
 Tom can choose from 7 different groups of two marbles.
Grading result: True
```

Note: You can show the agent's conversation history by uncommenting the bottom part. (the line 86-88)
