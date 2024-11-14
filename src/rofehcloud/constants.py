error_response = "It looks like we hit a snag. Please check your profile configuration and try again."

truncated_message = "(truncated)"

agent_prompt_with_history = f"""
Answer the following questions as best you can. You have access to the following tools:

{{tools}}

Use the following output format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I need to call tool 'Before final answer' once I'm ready to generate the final answer
Final Answer: the final answer to the original input question

IMPORTANT TIPS:
1. If you run a command and it doesn't work, try running a different command. A command that did not work 
once will not work the second time unless you modify it!
2. If you used an action tool with a specific action input and it returned an answer that was not helpful, 
do not use the tool again with the same input. Try a different input or a different tool.
3. Do not run the same query again on the same database to get more information. If you need more information
then try to ask a different question or use a different tool.
4. YAML files can have .yml or .yaml extensions.
5. If a tool response ends with text "{truncated_message}", it means the response is too long and has been 
truncated. Try to use the tool using a different input or filter the output to get a more concise response.

Begin!

Previous conversation history (from least recent to most recent):
{{chat_history}}

New input: {{input}}
Thought: {{agent_scratchpad}}
"""


data_modification_command_denied = (
    "SYSTEM ERROR: The proposed command is potentially risky and cannot be executed. "
    "Please suggest a different command that will not try to make any changes in the system. "
    "If an alternative command is not possible, please return an error message and stop sequence."
)
