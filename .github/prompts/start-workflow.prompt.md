---
description: "Hello promts"
arguments-hit: Give me you name
---
Following the requst from this prompt answer as 
Hello ${input}


Following the request to this prompt and split input into input1 and input2 (comma separated), answer as
Hello {input1: '${input1}', input2: '${input2}'}


---
name: test
description: Describe when to use this prompt
argument-hint: Provide name, greeting, and message.
---
Hello {{name}} have some, {{greeting}}, and {{message}} wishes to have a great day!