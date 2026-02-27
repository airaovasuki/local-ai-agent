import ollama
import os
from rich import print

MODEL = "llama3"

# ---- TOOLS ----

def read_file(filename):
    if not os.path.exists(filename):
        return "File not found."
    with open(filename, "r") as f:
        return f.read()

def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    return f"Written to {filename}"

TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
}

# ---- SYSTEM PROMPT ----

SYSTEM_PROMPT = """
You are an autonomous AI agent.

You can:
- read_file(filename)
- write_file(filename, content)

When you want to use a tool, respond EXACTLY like this:

TOOL: tool_name
INPUT: argument

If task is complete, respond:

DONE: explanation
"""

# ---- AGENT LOOP ----

def autonomous_agent(goal):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Your goal: {goal}"}
    ]

    for step in range(10):  # max 10 steps
        print(f"\n[bold yellow]Step {step+1}[/bold yellow]")

        response = ollama.chat(model=MODEL, messages=messages)
        content = response["message"]["content"]
        print("[white]", content)

        if content.startswith("DONE:"):
            print("\n[bold green]Goal completed.[/bold green]")
            break

        if content.startswith("TOOL:"):
            lines = content.split("\n")
            tool_name = lines[0].replace("TOOL:", "").strip()
            tool_input = lines[1].replace("INPUT:", "").strip()

            if tool_name in TOOLS:
                if tool_name == "write_file":
                    filename, filecontent = tool_input.split("|", 1)
                    result = TOOLS[tool_name](filename.strip(), filecontent.strip())
                else:
                    result = TOOLS[tool_name](tool_input)

                print("[green]Tool result:[/green]", result)

                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"Tool result: {result}"})
            else:
                print("[red]Unknown tool.[/red]")
                break
        else:
            messages.append({"role": "assistant", "content": content})

    else:
        print("[red]Max steps reached.[/red]")


if __name__ == "__main__":
    goal = input("Enter goal: ")
    autonomous_agent(goal)