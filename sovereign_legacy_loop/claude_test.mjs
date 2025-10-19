import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const res = await client.messages.create({
  model: "claude-3-5-sonnet-20240620",
  max_tokens: 128,
  messages: [{role:"user", content:"Reply with: Node SDK is wired up."}]
});
console.log(res.content[0].text);
